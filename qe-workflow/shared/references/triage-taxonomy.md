# Test Failure Triage Taxonomy

| Category | Meaning | Typical signals | Routed to |
|---|---|---|---|
| `product_bug` | The application behaves wrongly | Assertion on business value fails consistently; reproducible manually; recent app change in the area | defect-raising |
| `test_bug` | The test is wrong or outdated | Element not found after a UI change; wrong expected value due to a spec change; broken fixture | pipeline-self-heal (only locator/timing/data sub-types) or a manual fix |
| `environment` | Infra or a dependency is down or misconfigured | 5xx from a dependency, DNS/connection errors, expired certs, missing config | Notify the env/platform owner; re-run after the fix |
| `flaky` | Non-deterministic pass/fail with no code change | Passes on retry; history shows intermittent results; race or timing smell | Quarantine ticket + flaky-test owner (never silently retried forever) |
| `test_data` | Required data missing or in the wrong state | Record not found, unique constraint, expired account | Data refresh or self-heal (`test_data_refresh`) |

## test_bug sub-types (decide whether self-heal is allowed)

| Sub-type | Self-heal allowed? |
|---|---|
| `locator_drift` | Yes |
| `timing_wait` | Yes (explicit waits only, never fixed sleeps) |
| `test_data_refresh` | Yes |
| `assertion_outdated` | **No**: the expected behaviour changed. A human confirms with the PO first |
| `logic_error` | No |

## Confidence
Each classification carries `confidence` (high / medium / low) and the evidence used.
Low-confidence classifications go to a human and are never auto-routed.
