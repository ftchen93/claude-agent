# INV-310 Nightly stock reconciliation job

As an inventory manager, I want a nightly job that reconciles warehouse stock with the ERP so that stock discrepancies are flagged before the store opens.

## Acceptance criteria
- AC-1: Given the job runs at 02:00 UTC, when warehouse and ERP quantities for a SKU differ, then a discrepancy record is written with SKU, both quantities and the difference.
- AC-2: Given a difference greater than 5% of ERP quantity, then the discrepancy is marked "HIGH" and an alert is sent to the #inventory-alerts channel.
- AC-3: Given the ERP API is unavailable, the job retries 3 times at 5-minute intervals, then fails with status "ERP_UNAVAILABLE" and sends an alert.
- AC-4: Given no discrepancies, then the job completes with status "OK" and writes no records.
- AC-5: Running the job twice for the same date does not create duplicate records.

## Business rules
- Quantities compared at SKU + warehouse level. Differences of 0 are ignored.
- Discontinued SKUs (status D) are excluded.

## Scope
In scope: 3 EU warehouses. Out of scope: US warehouses, automatic correction.

## Dependencies / assumptions
ERP `GET /stock` v2; warehouse DB read replica; Slack webhook for alerts. Assumes fewer than 200k SKUs.

## NFR
Job finishes within 30 minutes for 200k SKUs.
