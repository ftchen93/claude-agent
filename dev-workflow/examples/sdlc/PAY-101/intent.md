# Intent: apply promo code at checkout
ID: PAY-101 · Author: A. Rivera (e-commerce marketing) · Status: accepted (PO, 2026-11-20) · Date: 2026-11-18

## Problem
Email campaigns advertise promo codes, but checkout has no field to enter them.
Customers contact support for manual refunds, about 300 tickets a month.

## Proposed outcome
Returning customers enter a code at web checkout and pay the advertised discounted price.

## Success measure
Promo refund tickets fall below 30 a month within one campaign cycle.

## Acceptance criteria (draft)
- AC-1: Given a cart of at least $20 and the valid code "SAVE10", when I apply it, then the total drops by 10%, rounded half up to 2 decimals, and a line "SAVE10 -$X.XX" is shown.
- AC-2: Given an expired code, when I apply it, then the total is unchanged and "This code has expired" is shown.
- AC-3: Given an unknown code, when I apply it, then "Code not recognised" is shown and the total is unchanged.
- AC-4: Given a cart below $20, when I apply a valid code, then "Minimum spend $20" is shown.
- AC-5: Only one code can be active; applying a second replaces the first.

## Affected users and systems
Returning customers; web checkout; promotions service (`GET /promotions/{code}`).

## Business rules and data
Codes are case-insensitive, up to 20 letters or digits. Discount applies to item subtotal only, not shipping or tax.

## Constraints
No new PII stored. Validation responds within 500 ms at p95.

## Out of scope
Mobile app, gift cards, stacking codes.

## Dependencies and assumptions
Promotions service is live in staging. Feature flag `checkout_promo`.

## Open questions
What happens if the cart drops below $20 after a code is applied?
