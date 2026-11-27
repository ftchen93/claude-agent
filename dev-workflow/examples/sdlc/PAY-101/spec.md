# Spec: apply promo code at checkout
ID: PAY-101 · From: intent.md (2026-11-20) · Status: accepted (PO, 2026-11-21) · Owner: PO e-commerce

## Summary
Add a promo code field to web checkout. The checkout service validates the code with the promotions service and applies a percentage discount to the item subtotal.

## Acceptance criteria
- AC-1: Given a cart subtotal of at least $20.00 and the valid, unexpired code "SAVE10", when I apply it, then the total is reduced by 10% of the subtotal, rounded half up to 2 decimals, and the line "SAVE10 -$X.XX" is shown.
- AC-2: Given an expired code, when I apply it, then the total is unchanged and "This code has expired" is shown under the field.
- AC-3: Given an unknown code, when I apply it, then "Code not recognised" is shown and the total is unchanged.
- AC-4: Given a subtotal below $20.00, when I apply a valid code, then "Minimum spend $20" is shown and no discount is applied.
- AC-5: Only one code can be active per order; applying a second replaces the first.
- AC-6: Given an applied code, when the subtotal drops below $20.00, then the code is removed and "Minimum spend $20" is shown. (Answers the open question from intent.md; PO decision 2026-11-21.)

## Functional requirements
- FR-1 (AC-1, AC-4, AC-6): `POST /checkout/{cartId}/promo` validates and applies a code; the discount is recalculated whenever the cart changes.
- FR-2 (AC-2, AC-3): error responses map to the exact messages above.
- FR-3 (AC-5): applying a code replaces any active code.

## Business rules and data
Codes are normalised to upper case and must match `^[A-Z0-9]{1,20}$`. The discount uses BigDecimal, half up. Nothing new is persisted beyond the order's applied code.

## Design
### Components and responsibilities
`checkout-api` adds the promo endpoint and recalculation; `web-checkout` adds the field and messages.
### Interfaces (API, events, UI)
`POST /checkout/{cartId}/promo {code}` returns 200 with totals, or 422 with `{reason: expired|unknown|min_spend}`.
### Data flow
UI → checkout-api → promotions service (cached 60 s per code) → totals.
### Error handling
If the promotions service is down, return 503 and the message "Codes can't be checked right now".

## Non-functional requirements
Validation p95 < 500 ms. Rate limit: 10 attempts per cart per minute (brute-force protection).

## Policy compliance
| Policy (skill) | Applied how | Status |
|---|---|---|
| secure-api-review | Gateway JWT on the endpoint; schema validation; audit event on apply | complies |
| accessibility | Error messages linked to the field with aria-describedby | complies |

## Areas of concern
1. The 60 s promotions cache could keep honouring a code for up to a minute after it expires. (owner: PO, decide if acceptable)
2. The rate limit could block a legitimate customer who mistypes repeatedly. (owner: security lead)

## Test strategy notes
Risky: rounding at boundaries, recalculation when the cart changes, the cache window. Test data: one valid, one expired and one unknown code in staging. Layers: API for rules, UI for messages.

## Out of scope
Mobile app, gift cards, stacking codes.

## Open questions
None open. The intent's question is answered by AC-6.
