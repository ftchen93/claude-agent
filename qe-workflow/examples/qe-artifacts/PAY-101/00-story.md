# PAY-101 Apply promo code at checkout

As a returning customer, I want to apply a promo code at checkout so that I pay the discounted price advertised in our email campaigns.

## Acceptance criteria
- AC-1: Given a cart totalling at least $20 and a valid, unexpired code "SAVE10", when I apply it, then the order total is reduced by 10%, rounded to 2 decimals (half up), and the discount line shows "SAVE10 -$X.XX".
- AC-2: Given an expired code, when I apply it, then the total is unchanged and the message "This code has expired" is shown under the field.
- AC-3: Given an unknown code, when I apply it, then the message "Code not recognised" is shown and the total is unchanged.
- AC-4: Given a cart below $20, when I apply a valid code, then the message "Minimum spend $20" is shown.
- AC-5: Only one promo code can be active per order; applying a second replaces the first.

## Business rules
- Codes are case-insensitive, max 20 characters, letters and digits only.
- The discount applies to item subtotal only, not shipping or tax.

## Scope
In scope: web checkout. Out of scope: mobile app, gift cards, stacking codes.

## Dependencies
Promotions service `GET /promotions/{code}` (already live in staging). Feature flag `checkout_promo`.

## NFR
Code validation responds within 500 ms at p95.

## Design
Figma: Checkout v3, frame "Promo field".
