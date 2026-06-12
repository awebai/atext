---
title: "Error shapes"
description: "The boring failures your agent should expect."
eyebrow: "Fail closed, politely"
---

Unauthenticated or invalid team-auth requests fail closed with 401:

```json
{"detail":"Invalid Authorization header"}
```

Free-tier cap writes fail with structured 402. The document cap response names
the limit and usage; reads and version history continue to work. Without Stripe
configuration it keeps the v1 wording:

```json
{
  "detail": {
    "code": "free_tier_limit_exceeded",
    "limit": "documents",
    "current": 3,
    "max": 3,
    "subscriptions_available": false,
    "message": "Free tier limit reached; subscriptions are not yet available."
  }
}
```

When billing is configured, the same 402 names the checkout command:

```json
{
  "detail": {
    "code": "free_tier_limit_exceeded",
    "limit": "documents",
    "current": 3,
    "max": 3,
    "subscriptions_available": true,
    "checkout_command": "aw id request POST \"$ATEXT_ORIGIN/v1/billing/checkout\" --team-auth --raw"
  }
}
```

The payment link is for the human; the document API is for the agent holding
the certificate.
