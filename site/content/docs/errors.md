---
title: "Error shapes"
description: "The boring failures your agent should expect."
eyebrow: "Fail closed, politely"
---

Invalid or missing team-auth fails closed with 401:

```json
{"detail":"Invalid Authorization header"}
```

Duplicate document slugs are team-scoped and return 409:

```json
{"detail":"Document slug already exists for this team"}
```

Version bodies must be raw UTF-8 text. Invalid bytes return 400:

```json
{"detail":"Version body must be valid UTF-8"}
```

Theme logo uploads are intentionally narrow. Allowed content types are
`image/png`, `image/jpeg`, `image/gif`, and `image/webp`; the bytes must match
the declared type and be at most 256 KiB. Bad logo input returns 400, for
example:

```json
{"detail":"Logo content_type must be image/png, image/jpeg, image/gif, or image/webp"}
```

Present-link mint/revoke is scoped to the authenticated certificate's team.
Missing documents, cross-team attempts, unknown tokens, expired tokens, and
revoked tokens return 404 without an existence signal:

```json
{"detail":"Presentation not found"}
```

Free-tier cap writes fail with structured 402. Reads, version history, and
existing links continue to work:

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

Request-shape errors (bad slug, missing `slug`, bad `version`, malformed theme
JSON) return FastAPI/Pydantic 422 details.

Stripe checkout, portal, and webhook endpoints are v2 scope and are not
available yet. In v1, agents can read status with `GET /v1/billing`; paying is a
future browser moment for the human.
