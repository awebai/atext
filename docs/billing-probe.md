# Stripe test-mode billing probe

This is the human-pays validation for v2 billing: **402 → pay → 200** with
real Stripe test-mode infrastructure. Run it only when Juan provides test-mode
Stripe keys.

## Prerequisites

- Released `aw` CLI with `aw id request --team-auth`.
- Docker and the local e2e stack from this repo.
- Stripe CLI logged in to the same test-mode account, or dashboard webhook
  forwarding configured.
- Test-mode Stripe secret key and webhook signing secret.
- A test-mode recurring Price id for a team subscription.

## 1. Configure billing

```bash
export ATEXT_ORIGIN="http://127.0.0.1:8765"
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
export ATEXT_STRIPE_PRICE_ID="price_..."
```

If you need to create a disposable test price:

```bash
stripe products create --name "atext team" --default-price-data \
  "currency=usd" \
  "unit_amount=1000" \
  "recurring[interval]=month"
```

Use the returned default price id as `ATEXT_STRIPE_PRICE_ID`.

## 2. Start atext and webhook forwarding

Run atext with the environment above and a reachable public origin for the
agent request signature. In another terminal, forward Stripe events to the
local webhook:

```bash
stripe listen --forward-to "$ATEXT_ORIGIN/v1/stripe/webhook"
```

If `stripe listen` prints a new `whsec_...`, use that value for
`STRIPE_WEBHOOK_SECRET` and restart atext.

## 3. Prepare a real team-auth workspace

Use the README setup flow (identity, team, certificate, active team). Then fill
the free document cap:

```bash
aw id request POST "$ATEXT_ORIGIN/v1/documents" --team-auth --raw \
  --body '{"slug":"cap-1","title":"Cap 1","body":"one"}'
aw id request POST "$ATEXT_ORIGIN/v1/documents" --team-auth --raw \
  --body '{"slug":"cap-2","title":"Cap 2","body":"two"}'
aw id request POST "$ATEXT_ORIGIN/v1/documents" --team-auth --raw \
  --body '{"slug":"cap-3","title":"Cap 3","body":"three"}'
```

The next create must return 402 and name the checkout command:

```bash
aw id request POST "$ATEXT_ORIGIN/v1/documents" --team-auth --raw \
  --body '{"slug":"cap-4","title":"Cap 4","body":"blocked"}'
```

## 4. Checkout, human pays, caps lift

Create the checkout link:

```bash
aw id request POST "$ATEXT_ORIGIN/v1/billing/checkout" --team-auth --raw
```

Open the returned `checkout_url` in a browser and pay with Stripe's test card:

```text
4242 4242 4242 4242
any future expiry
any CVC
any ZIP
```

Wait for the forwarded `checkout.session.completed` event to reach atext.
Then the same team can create past the free cap without changing clients:

```bash
aw id request POST "$ATEXT_ORIGIN/v1/documents" --team-auth --raw \
  --body '{"slug":"paid-works","title":"Paid works","body":"caps lifted"}'
```

Confirm billing status:

```bash
aw id request GET "$ATEXT_ORIGIN/v1/billing" --team-auth --raw
```

Expected tier is `active` and caps are unlimited (`null`).

## 5. Portal cancellation returns caps

Open the portal link:

```bash
aw id request POST "$ATEXT_ORIGIN/v1/billing/portal" --team-auth --raw
```

Cancel the subscription in the Stripe portal. Wait for the forwarded
`customer.subscription.deleted` or canceled subscription update. Billing status
should return to `free`, and new writes beyond the free caps should again fail
with structured 402.

## Probe exit criteria

The probe is complete only when all are observed against real Stripe test mode:

1. Free team hits 402 at the cap.
2. Checkout link is created by a signed team-auth request.
3. Human pays in Stripe Checkout.
4. Stripe webhook activates the team subscription.
5. A write that previously failed now succeeds with no client change.
6. Portal cancellation returns the team to free-tier enforcement.
