from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from billing_events import sign_stripe_event, stripe_event
from fastapi import HTTPException

from atext import billing

WEBHOOK_SECRET = "whsec_e2e_synthetic"


class FakeTransaction:
    def __init__(self, db: FakeBillingDB) -> None:
        self.db = db

    async def __aenter__(self) -> FakeTransaction:
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    async def fetch_one(self, sql: str, *args: Any) -> dict[str, Any] | None:
        return await self.db.fetch_one(sql, *args)

    async def execute(self, sql: str, *args: Any) -> None:
        await self.db.execute(sql, *args)


class FakeBillingDB:
    def __init__(self) -> None:
        self.subscriptions: dict[str, dict[str, Any]] = {}

    def transaction(self) -> FakeTransaction:
        return FakeTransaction(self)

    async def fetch_one(self, sql: str, *args: Any) -> dict[str, Any] | None:
        compact = " ".join(sql.split())
        if "WHERE team_id = $1" in compact:
            return self.subscriptions.get(str(args[0]))
        if "WHERE stripe_subscription_id = $1" in compact:
            subscription_id = str(args[0])
            return next(
                (
                    row
                    for row in self.subscriptions.values()
                    if row.get("stripe_subscription_id") == subscription_id
                ),
                None,
            )
        raise AssertionError(f"unexpected fetch_one SQL: {compact}")

    async def execute(self, sql: str, *args: Any) -> None:
        compact = " ".join(sql.split())
        if compact.startswith("INSERT INTO {{tables.subscriptions}}"):
            team_id, customer_id, subscription_id, event_id, event_created_at = args
            row = self.subscriptions.setdefault(
                str(team_id),
                {
                    "team_id": str(team_id),
                    "tier": "free",
                    "stripe_customer_id": None,
                    "stripe_subscription_id": None,
                    "current_period_end": None,
                    "last_event_id": None,
                    "last_event_created_at": None,
                },
            )
            row.update(
                {
                    "tier": "active",
                    "stripe_customer_id": customer_id or row.get("stripe_customer_id"),
                    "stripe_subscription_id": subscription_id,
                    "last_event_id": event_id,
                    "last_event_created_at": event_created_at,
                }
            )
            return
        if compact.startswith("UPDATE {{tables.subscriptions}}"):
            team_id, tier, customer_id, period_end, event_id, event_created_at = args
            row = self.subscriptions[str(team_id)]
            row.update(
                {
                    "tier": tier,
                    "stripe_customer_id": customer_id or row.get("stripe_customer_id"),
                    "current_period_end": period_end or row.get("current_period_end"),
                    "last_event_id": event_id,
                    "last_event_created_at": event_created_at,
                }
            )
            return
        raise AssertionError(f"unexpected execute SQL: {compact}")


def test_signed_event_helper_uses_real_stripe_hmac() -> None:
    event = stripe_event("checkout.session.completed", {}, event_id="evt_sig", created=1_700_000_000)
    body, header = sign_stripe_event(event, WEBHOOK_SECRET, timestamp=1_700_000_010)

    assert billing.verify_webhook_signature(body, header, WEBHOOK_SECRET, now=1_700_000_010)
    assert not billing.verify_webhook_signature(body + b"x", header, WEBHOOK_SECRET, now=1_700_000_010)
    assert not billing.verify_webhook_signature(body, header, WEBHOOK_SECRET, now=1_700_000_311)
    fresh_body, fresh_header = sign_stripe_event(event, WEBHOOK_SECRET)
    assert billing.parse_signed_event(fresh_body, fresh_header, WEBHOOK_SECRET) == event


def test_parse_signed_event_rejects_bad_signature() -> None:
    body, _header = sign_stripe_event(stripe_event("checkout.session.completed", {}), WEBHOOK_SECRET)

    with pytest.raises(HTTPException) as raised:
        billing.parse_signed_event(body, "t=1,v1=deadbeef", WEBHOOK_SECRET)

    assert raised.value.status_code == 400
    assert raised.value.detail == {"error": "INVALID_SIGNATURE"}


@pytest.mark.asyncio
async def test_checkout_activation_replay_past_due_cancel_and_reupgrade() -> None:
    db = FakeBillingDB()

    completed = stripe_event(
        "checkout.session.completed",
        {"client_reference_id": "team_1", "subscription": "sub_1", "customer": "cus_1"},
        event_id="evt_checkout",
        created=100,
    )
    assert await billing.handle_stripe_event(db, completed) == "applied"
    assert db.subscriptions["team_1"]["tier"] == "active"
    assert db.subscriptions["team_1"]["stripe_customer_id"] == "cus_1"
    assert db.subscriptions["team_1"]["stripe_subscription_id"] == "sub_1"

    assert await billing.handle_stripe_event(db, completed) == "duplicate"
    assert len(db.subscriptions) == 1

    past_due = stripe_event(
        "customer.subscription.updated",
        {"id": "sub_1", "status": "past_due", "current_period_end": 1_700_000_000},
        event_id="evt_past_due",
        created=200,
    )
    assert await billing.handle_stripe_event(db, past_due) == "applied"
    assert db.subscriptions["team_1"]["tier"] == "past_due"
    assert db.subscriptions["team_1"]["current_period_end"] == datetime.fromtimestamp(1_700_000_000, tz=UTC)

    stale_active = stripe_event(
        "customer.subscription.updated",
        {"id": "sub_1", "status": "active"},
        event_id="evt_stale_active",
        created=150,
    )
    assert await billing.handle_stripe_event(db, stale_active) == "duplicate"
    assert db.subscriptions["team_1"]["tier"] == "past_due"

    deleted = stripe_event(
        "customer.subscription.deleted",
        {"id": "sub_1", "status": "canceled"},
        event_id="evt_deleted",
        created=300,
    )
    assert await billing.handle_stripe_event(db, deleted) == "applied"
    assert db.subscriptions["team_1"]["tier"] == "free"

    newer_stale_active = stripe_event(
        "customer.subscription.updated",
        {"id": "sub_1", "status": "active"},
        event_id="evt_after_deleted_active",
        created=400,
    )
    assert await billing.handle_stripe_event(db, newer_stale_active) == "duplicate"
    assert db.subscriptions["team_1"]["tier"] == "free"

    assert await billing.handle_stripe_event(db, completed) == "duplicate"
    assert db.subscriptions["team_1"]["tier"] == "free"

    reupgrade = stripe_event(
        "checkout.session.completed",
        {"client_reference_id": "team_1", "subscription": "sub_2", "customer": "cus_1"},
        event_id="evt_recheckout",
        created=500,
    )
    assert await billing.handle_stripe_event(db, reupgrade) == "applied"
    assert db.subscriptions["team_1"]["tier"] == "active"
    assert db.subscriptions["team_1"]["stripe_subscription_id"] == "sub_2"


@pytest.mark.asyncio
async def test_unknown_subscription_update_is_ignored() -> None:
    db = FakeBillingDB()
    unknown = stripe_event(
        "customer.subscription.updated",
        {"id": "sub_unknown", "status": "active"},
        event_id="evt_unknown",
        created=100,
    )

    assert await billing.handle_stripe_event(db, unknown) == "ignored"
    assert db.subscriptions == {}
