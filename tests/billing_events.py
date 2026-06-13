from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any


def sign_stripe_event(
    payload: dict[str, Any],
    secret: str,
    *,
    timestamp: int | None = None,
) -> tuple[bytes, str]:
    """Return Stripe-style webhook bytes and signature header.

    Stripe signs the exact request bytes over ``<timestamp>.<payload>`` with
    HMAC-SHA256 using the endpoint secret. Tests use this helper so the
    service's real verifier runs; they do not mock signature verification.
    """

    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    ts = int(time.time()) if timestamp is None else timestamp
    signed = f"{ts}.".encode("ascii") + body
    signature = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    return body, f"t={ts},v1={signature}"


def stripe_event(
    kind: str,
    obj: dict[str, Any],
    *,
    event_id: str = "evt_e2e",
    created: int | None = None,
) -> dict[str, Any]:
    event_created = int(time.time()) if created is None else created
    return {
        "id": event_id,
        "object": "event",
        "created": event_created,
        "type": kind,
        "data": {"object": obj},
    }
