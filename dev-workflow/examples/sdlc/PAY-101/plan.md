# Plan: apply promo code at checkout (from spec.md 2026-11-21)
ID: PAY-101 · Engineer: S. Okafor · Status: accepted (by S. Okafor, 2026-11-22)

## Files that change
checkout-api/src/promo/PromoController.java (new) - the endpoint
checkout-api/src/promo/PromoService.java (new) - validation, discount, recalculation
checkout-api/src/cart/CartService.java (changed) - recalculate on cart change (AC-6)
checkout-api/src/itest/promo/PromoApiIT.java (new) - API tests for TC-001..007
web-checkout/src/checkout/PromoField.tsx (new) - field and messages
web-checkout/tests/promo.spec.ts (new) - UI tests for TC-001, TC-003

## Order of work
1. PromoService with rounding and rules, which proves TC-001, TC-002, TC-005
2. Endpoint with error mapping, which proves TC-003, TC-004
3. Replace-on-apply, which proves TC-006
4. Recalculation on cart change, which proves TC-007
5. UI field and messages, which proves TC-001 and TC-003 end to end

## Risks
- Cache window (spec concern 1): keep the 60 s TTL configurable; default per the PO decision.
- Double discount if recalculation and apply race: apply and recalc share one lock per cart.

## Alternatives considered
- Validating codes in the UI only: rejected, because it can be bypassed.

## Proof
- Command: `make itest TESTS=PromoApiIT`
- Command: `npx playwright test tests/promo.spec.ts`
- TC-001 (AC-1): PromoApiIT::TC-001 and promo.spec.ts::TC-001
- TC-002 (AC-1): PromoApiIT::TC-002
- TC-003 (AC-2): PromoApiIT::TC-003 and promo.spec.ts::TC-003
- TC-004 (AC-3): PromoApiIT::TC-004
- TC-005 (AC-4): PromoApiIT::TC-005
- TC-006 (AC-5): PromoApiIT::TC-006
- TC-007 (AC-6): PromoApiIT::TC-007
- Manual / exploratory: TC-008, run by QE in staging after deploy

## Deviations
None yet.
