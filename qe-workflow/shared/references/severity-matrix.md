# Defect Severity Matrix

Severity = impact on the product. Priority = urgency to fix (set by the PO; the skill only
suggests it).

| Severity | Definition | Examples |
|---|---|---|
| Critical | System unusable, data loss or corruption, security breach, legal/compliance exposure; no workaround | Payments fail for all users; PII exposed |
| High | Major feature broken or wrong results; workaround is hard or not acceptable | Discount calculated wrongly; cannot submit form in one browser |
| Medium | Feature partly broken; reasonable workaround exists | Filter ignores one option; export misses a column |
| Low | Cosmetic or minor usability issue | Misaligned label; typo |

Raise severity one level when the defect affects a regulated flow or a high-traffic path.
