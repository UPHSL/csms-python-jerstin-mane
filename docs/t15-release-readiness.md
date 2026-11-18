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

The five hardening additions were implemented as automated tests. The service request form template was also modified during T15 to remove navigation links from the new request form.

## 4. Five New T15 Hardening Tests

| Test Name | Category | What It Verifies | Additional Value |
|---|---|---|---|
| test_malformed_resident_id_submission_is_rejected_without_saving | Invalid or malformed input | A non-numeric resident ID is rejected without saving a request | Tests malformed input through the actual UI route |
| test_rejected_terminal_request_mutation_preserves_record | Rejected mutation protects persistence | A Completed request remains unchanged after an invalid transition attempt | Checks all persisted request fields, not only the response |
| test_repeated_request_detail_gets_preserve_all_persisted_fields | Read-only request safety | Repeated detail GET requests do not change stored request data | Checks persistence after repeated access |
| test_resident_registration_request_submission_and_dashboard_work_together | Cross-feature regression | A registered resident can submit a request and the dashboard displays it | Checks integration across three application features |
| test_sql_injection_like_search_input_does_not_return_unrelated_requests | Query safety | SQL-injection-like search input does not return unrelated requests | Checks search behavior at an unusual input boundary |

## 5. Full Regression Results

Command:

`.\.venv\Scripts\python.exe -m pytest`

| Regression Run | Result | Duration |
|---|---:|---:|
| Run 1 | 177 passed, 0 failed | 100.59 seconds |
| Run 2 | 177 passed, 0 failed | 113.36 seconds |
| Run 3 | 177 passed, 0 failed | 90.50 seconds |

- Starter-T14 baseline: 172 passed
- T15 new tests: 5 passed
- Current total: 177 passed
- All three full regression runs completed successfully.

## 6. Manual Release Verification

The following checks were completed against the running application.

| Manual Check | Status | Notes |
|---|---|---|
| Application starts successfully | PASS | Flask application started successfully |
| `/health` returns an OK response | PASS | Returned application identity, status ok, and version 0.1.0 |
| Dashboard loads | PASS | Dashboard opened successfully |
| Resident listing and search work | PASS | Resident list and search verified |
| Valid resident registration works | PASS | Test resident registered successfully |
| Invalid resident registration is rejected | PASS | Required-field and email validation verified |
| Resident information can be updated | PASS | Updated test resident successfully |
| Resident deactivation works | PASS | Test resident deactivated successfully |
| Valid request submission for an Active resident works | PASS | Request successfully created |
| Inactive resident submission is rejected | PASS | Submission using inactive Resident ID 2 was rejected |
| Request search, filtering, and details work | PASS | Search, Pending filter, and details page verified |
| Valid request workflow transitions work | PASS | Pending to In Progress to Completed |
| Terminal workflow actions are unavailable | PASS | Completed request displayed only View; automated T15 test verifies rejected mutations preserve the record |
| Dashboard reflects resident and request changes | PASS | Updated request information appeared |
| Read-only request details are protected | PASS | Automated T15 test verified repeated detail GET requests preserve persisted fields |
| Missing records are handled safely | PASS | Missing resident and request returned 404 |
| Navigation links work | PASS | Dashboard navigation links verified |

## 7. Repository Hygiene Review

The following repository checks were completed:

| Review Item | Status |
|---|---|
| Debug output and temporary files | PASS - No debug print statements or TODO/FIXME markers found |
| Generated artifacts and accidental database files | PASS - No tracked cache, bytecode, or database files found |
| Abandoned commented-out code | REVIEWED |
| Exposed credentials or secrets | PASS - No actual credentials found; production must provide CSMS_SECRET_KEY |
| Broken navigation links | PASS - Template navigation uses Flask url_for(); dashboard navigation links manually verified |
| Parameterized SQL queries | REVIEWED IN SERVICE REQUEST REPOSITORY |
| Test reliability and repeatability | PASS - Three full regression runs completed |
| Git formatting and whitespace | PASS - git diff --check returned no errors |
| Git working tree | PASS - Clean working tree before this report update |

## 8. Known Limitations

- Deactivated residents cannot be reactivated through the current application. Resident reactivation is outside the defined T16 scope.
- The development configuration includes a fallback secret key. Production deployments must provide a strong secret value through the CSMS_SECRET_KEY environment variable.

These limitations do not prevent the project from proceeding to the T16 final exam within its defined scope.

## 9. Release Candidate Statement

READY FOR T16 FINAL EXAM

The automated regression suite passed three times with 177 tests and no failures. The manual application checks and repository hygiene review were also completed. The T15 implementation is ready to proceed to the T16 final exam within the defined project scope.