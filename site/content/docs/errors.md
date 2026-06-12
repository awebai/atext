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
the limit and usage; reads and version history continue to work:

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

Stripe checkout, portal, and webhook endpoints are v2 scope and are not available
in v1. The future payment link is for the human; the document API is for the
agent holding the certificate.
