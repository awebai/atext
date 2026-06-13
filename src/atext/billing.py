from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import time
from datetime import UTC, datetime
from typing import Any, Protocol

from fastapi import HTTPException
from pgdbm import AsyncDatabaseManager

from atext.config import Settings

SIGNATURE_TOLERANCE_SECONDS = 300
ACTIVE_STRIPE_STATUSES = {"active", "trialing"}
PAST_DUE_STRIPE_STATUSES = {"past_due"}
TERMINAL_STRIPE_STATUSES = {"canceled", "unpaid", "incomplete_expired"}


class BillingProvider(Protocol):
    async def checkout_url(self, *, team_id: str, settings: Settings) -> str: ...

    async def portal_url(self, *, customer_id: str, settings: Settings) -> str: ...


class SyntheticStripeBillingProvider:
    """No-network Stripe-shaped provider for synthetic e2e configuration."""

    async def checkout_url(self, *, team_id: str, settings: Settings) -> str:
        return f"https://checkout.stripe.test/{team_id}"

    async def portal_url(self, *, customer_id: str, settings: Settings) -> str:
        return f"https://billing.stripe.test/{customer_id}"


class StripeBillingProvider:
    def __init__(self, secret_key: str) -> None:
        import stripe

        self._client: Any = stripe.StripeClient(secret_key)

    async def checkout_url(self, *, team_id: str, settings: Settings) -> str:
        def create() -> str:
            session = self._client.checkout.sessions.create(
                params={
                    "mode": "subscription",
                    "line_items": [{"price": settings.stripe_price_id, "quantity": 1}],
                    "client_reference_id": team_id,
                    "success_url": f"{settings.public_origin.rstrip('/')}/billing/success",
                    "cancel_url": f"{settings.public_origin.rstrip('/')}/billing/cancelled",
                }
            )
            return str(session.url)

        return await asyncio.get_running_loop().run_in_executor(None, create)

    async def portal_url(self, *, customer_id: str, settings: Settings) -> str:
        def create() -> str:
            session = self._client.billing_portal.sessions.create(
                params={
                    "customer": customer_id,
                    "return_url": f"{settings.public_origin.rstrip('/')}/billing/portal-return",
                }
            )
            return str(session.url)

        return await asyncio.get_running_loop().run_in_executor(None, create)


def checkout_configured(settings: Settings) -> bool:
    return bool(settings.stripe_secret_key and settings.stripe_price_id)


def synthetic_stripe_configured(settings: Settings) -> bool:
    return bool(
        str(settings.stripe_secret_key or "").startswith("sk_test_e2e_")
        or str(settings.stripe_price_id or "").startswith("price_e2e_")
    )


def provider_for_settings(settings: Settings) -> BillingProvider:
    if synthetic_stripe_configured(settings):
        return SyntheticStripeBillingProvider()
    return StripeBillingProvider(str(settings.stripe_secret_key))


def webhook_configured(settings: Settings) -> bool:
    return bool(settings.stripe_webhook_secret)


def checkout_recipe(settings: Settings) -> str:
    return 'aw id request POST "$ATEXT_ORIGIN/v1/billing/checkout" --team-auth --raw'


def billing_not_available_detail() -> dict[str, Any]:
    return {
        "code": "billing_not_configured",
        "subscriptions_available": False,
        "message": "Subscriptions are not yet available.",
    }


def verify_webhook_signature(
    payload: bytes,
    header: str,
    secret: str,
    *,
    now: float | None = None,
) -> bool:
    timestamp = ""
    candidates: list[str] = []
    for part in (header or "").split(","):
        key, _, value = part.strip().partition("=")
        if key == "t":
            timestamp = value
        elif key == "v1":
            candidates.append(value)
    if not timestamp or not candidates:
        return False
    try:
        ts = int(timestamp)
    except ValueError:
        return False
    if abs((time.time() if now is None else now) - ts) > SIGNATURE_TOLERANCE_SECONDS:
        return False
    expected = hmac.new(secret.encode("utf-8"), f"{timestamp}.".encode() + payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, candidate) for candidate in candidates)


def parse_signed_event(payload: bytes, signature: str, secret: str) -> dict[str, Any]:
    if not verify_webhook_signature(payload, signature, secret):
        raise HTTPException(status_code=400, detail={"error": "INVALID_SIGNATURE"})
    try:
        event = json.loads(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": "INVALID_PAYLOAD"}) from exc
    if not isinstance(event, dict):
        raise HTTPException(status_code=400, detail={"error": "INVALID_PAYLOAD"})
    return event


def stripe_status_to_tier(status: str, *, deleted: bool = False) -> str:
    if deleted:
        return "free"
    normalized = status.strip().lower()
    if normalized in ACTIVE_STRIPE_STATUSES:
        return "active"
    if normalized in PAST_DUE_STRIPE_STATUSES:
        return "past_due"
    if normalized in TERMINAL_STRIPE_STATUSES:
        return "free"
    return "free"


def _event_created_at(event: dict[str, Any]) -> datetime | None:
    created = event.get("created")
    if isinstance(created, (int, float)) and created > 0:
        return datetime.fromtimestamp(created, tz=UTC)
    return None


def _period_end(value: Any) -> datetime | None:
    if isinstance(value, (int, float)) and value > 0:
        return datetime.fromtimestamp(value, tz=UTC)
    return None


def _row_value(row: Any, key: str) -> Any:
    try:
        return row[key]
    except (KeyError, TypeError):
        return None


def _is_newer_event(row: Any, *, event_id: str, event_created_at: datetime | None) -> bool:
    if row is None:
        return True
    if str(_row_value(row, "last_event_id") or "") == event_id:
        return False
    last_created = _row_value(row, "last_event_created_at")
    if isinstance(last_created, datetime) and event_created_at is not None and last_created > event_created_at:
        return False
    return True


async def handle_stripe_event(db: AsyncDatabaseManager, event: dict[str, Any]) -> str:
    event_id = str(event.get("id") or "").strip()
    kind = str(event.get("type") or "").strip()
    obj = (event.get("data") or {}).get("object") or {}
    if not event_id or not isinstance(obj, dict):
        return "ignored"
    if kind == "checkout.session.completed":
        return await apply_checkout_completed(db, event_id=event_id, event_created_at=_event_created_at(event), session=obj)
    if kind == "customer.subscription.updated":
        return await apply_subscription_state(db, event_id=event_id, event_created_at=_event_created_at(event), subscription=obj, deleted=False)
    if kind == "customer.subscription.deleted":
        return await apply_subscription_state(db, event_id=event_id, event_created_at=_event_created_at(event), subscription=obj, deleted=True)
    return "ignored"


async def apply_checkout_completed(
    db: AsyncDatabaseManager,
    *,
    event_id: str,
    event_created_at: datetime | None,
    session: dict[str, Any],
) -> str:
    team_id = str(session.get("client_reference_id") or "").strip()
    subscription_id = str(session.get("subscription") or "").strip()
    customer_id = str(session.get("customer") or "").strip() or None
    if not team_id or not subscription_id:
        return "ignored"
    async with db.transaction() as tx:
        row = await tx.fetch_one("SELECT * FROM {{tables.subscriptions}} WHERE team_id = $1 FOR UPDATE", team_id)
        if not _is_newer_event(row, event_id=event_id, event_created_at=event_created_at):
            return "duplicate"
        if row is not None and _row_value(row, "stripe_subscription_id") == subscription_id and _row_value(row, "tier") == "free":
            return "duplicate"
        await tx.execute(
            """
            INSERT INTO {{tables.subscriptions}}
              (team_id, tier, stripe_customer_id, stripe_subscription_id, current_period_end, last_event_id, last_event_created_at)
            VALUES ($1, 'active', $2, $3, NULL, $4, $5)
            ON CONFLICT (team_id) DO UPDATE
            SET tier = 'active',
                stripe_customer_id = COALESCE(EXCLUDED.stripe_customer_id, {{tables.subscriptions}}.stripe_customer_id),
                stripe_subscription_id = EXCLUDED.stripe_subscription_id,
                last_event_id = EXCLUDED.last_event_id,
                last_event_created_at = EXCLUDED.last_event_created_at,
                updated_at = NOW()
            """,
            team_id,
            customer_id,
            subscription_id,
            event_id,
            event_created_at,
        )
    return "applied"


async def apply_subscription_state(
    db: AsyncDatabaseManager,
    *,
    event_id: str,
    event_created_at: datetime | None,
    subscription: dict[str, Any],
    deleted: bool,
) -> str:
    subscription_id = str(subscription.get("id") or "").strip()
    if not subscription_id:
        return "ignored"
    tier = stripe_status_to_tier(str(subscription.get("status") or ""), deleted=deleted)
    period_end = _period_end(subscription.get("current_period_end"))
    customer_id = str(subscription.get("customer") or "").strip() or None
    async with db.transaction() as tx:
        row = await tx.fetch_one(
            "SELECT * FROM {{tables.subscriptions}} WHERE stripe_subscription_id = $1 FOR UPDATE",
            subscription_id,
        )
        if row is None:
            return "ignored"
        if not _is_newer_event(row, event_id=event_id, event_created_at=event_created_at):
            return "duplicate"
        if _row_value(row, "tier") == "free" and not deleted:
            return "duplicate"
        await tx.execute(
            """
            UPDATE {{tables.subscriptions}}
            SET tier = $2,
                stripe_customer_id = COALESCE($3, stripe_customer_id),
                current_period_end = COALESCE($4, current_period_end),
                last_event_id = $5,
                last_event_created_at = $6,
                updated_at = NOW()
            WHERE team_id = $1
            """,
            row["team_id"],
            tier,
            customer_id,
            period_end,
            event_id,
            event_created_at,
        )
    return "applied"
