# T15 - System Hardening and Regression Testing
## Release Readiness Report

## 1. Developer Information

- Name: Jerstin Mangahis Mane
- GitHub Username: jerstin-mane
- Technology Stack: Python 3.13, Flask 3.1, SQLite, pytest
- Branch: feature/t15-system-hardening
- Repository: https://github.com/UPHSL/csms-python-jerstin-mane

## 2. Release Candidate Baseline

The existing T01-T14 implementation was tested before T15 changes.

| Baseline Check | Result |
|---|---|
| Application startup | Previously verified |
| Health endpoint | Previously verified |
| Dashboard | Previously verified |
| Resident management | Previously verified |
| Service Request management | Previously verified |
| Starter-T14 automated tests | 172 passed |

## 3. Hardening Changes

| Area | Issue or Risk Found | Action Taken | Files Changed | Test or Evidence |
|---|---|---|---|---|
| Malformed input | Non-numeric resident ID submitted through the Service Request form | Added a test confirming rejection without creating a request | tests/test_t15_hardening.py | Malformed resident ID test passed |
| Persistence integrity | A terminal request must not accept another workflow transition | Added a test confirming that a rejected mutation preserves all stored fields | tests/test_t15_hardening.py | Terminal request mutation test passed |
| Read-only request safety | Repeated detail page access must not modify stored request information | Added a test comparing all persisted fields before and after repeated GET requests | tests/test_t15_hardening.py | Repeated detail GET test passed |
| Cross-feature integration | Resident registration, request submission, and dashboard display must work together | Added an integration test covering the complete workflow | tests/test_t15_hardening.py | Cross-feature workflow test passed |
| Query safety | Search input containing SQL-injection-like text must not return unrelated records | Added a test confirming the input is treated as search data | tests/test_t15_hardening.py | SQL-injection-like search test passed |

No application source code changes were required for these five additions.

## 4. Five New T15 Hardening Tests

| Test Name | Category | What It Verifies | Additional Value |
|---|---|---|---|
| test_malformed_resident_id_submission_is_rejected_without_saving | Invalid or malformed input | A non-numeric resident ID is rejected without saving a request | Tests malformed input through the actual UI route |
| test_rejected_terminal_request_mutation_preserves_record | Rejected mutation protects persistence | A Completed request remains unchanged after an invalid transition attempt | Checks all persisted request fields, not only the response |
| test_repeated_request_detail_gets_preserve_all_persisted_fields | Read-only request safety | Repeated detail GET requests do not change stored request data | Checks persistence after repeated access |
| test_resident_registration_request_submission_and_dashboard_work_together | Cross-feature regression | A registered resident can submit a request and the dashboard displays it | Checks integration across three application features |
| test_sql_injection_like_search_input_does_not_return_unrelated_requests | Repeatability or boundary behavior | SQL-injection-like search input does not return unrelated requests | Checks search behavior at an unusual input boundary |

## 5. Full Regression Results

Command:

`.\.venv\Scripts\python.exe -m pytest`

| Regression Run | Result | Duration |
|---|---:|---:|
| Run 1 | 177 passed, 0 failed | 100.59 seconds |
| Run 2 | 177 passed, 0 failed | 113.36 seconds |

- Starter-T14 baseline: 172 passed
- T15 new tests: 5 passed
- Current total: 177 passed
- Both full regression runs completed successfully.

## 6. Manual Release Verification

Complete these checks against the running application before marking the release candidate ready.

| Manual Check | Status | Notes |
|---|---|---|
| Application starts successfully | PENDING | |
| `/health` returns an OK response | PENDING | |
| Dashboard loads | PENDING | |
| Resident listing and search work | PENDING | |
| Valid resident registration works | PENDING | |
| Invalid resident registration is rejected | PENDING | |
| Resident information can be updated | PENDING | |
| Resident deactivation works and the record remains visible | PENDING | |
| Valid request submission for an Active resident works | PENDING | |
| Missing or Inactive resident submission is rejected | PENDING | |
| Request search, filtering, and details work | PENDING | |
| Valid request workflow transitions work | PENDING | |
| Invalid and terminal transitions are rejected | PENDING | |
| Dashboard reflects resident and request changes | PENDING | |
| GET/read-only pages do not modify persisted data | PENDING | |
| Missing records are handled safely | PENDING | |
| Navigation links work across the application | PENDING | |

## 7. Repository Hygiene Review

The following items require a final repository inspection before release:

| Review Item | Status |
|---|---|
| Debug output and temporary files | PENDING |
| Generated artifacts and accidental database files | PENDING |
| Abandoned commented-out code | PENDING |
| Exposed credentials or secrets | PENDING |
| Broken navigation links | PENDING |
| Parameterized SQL queries | REVIEWED IN SERVICE REQUEST REPOSITORY |
| Test reliability and repeatability | PASS - TWO FULL REGRESSION RUNS |

## 8. Known Limitations

No known release-blocking limitations identified within the defined CSMS scope.

## 9. Release Candidate Statement

NOT YET READY FOR T16 FINAL EXAM

The automated regression suite passed twice with 177 tests. Manual release verification and the final repository hygiene review must still be completed before the release candidate can be declared ready.
