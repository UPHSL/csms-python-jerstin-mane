# T16 - Final Examination
## Final Project Checkpoint

## 1. Developer Information

- Name: Jerstin Mangahis Mane
- GitHub Username: jerstin-mane
- Technology Stack: Python 3.13, Flask 3.1, SQLite, pytest
- Branch: feature/t16-final-release
- Repository: https://github.com/UPHSL/csms-python-jerstin-mane
- Final Release Version: 1.0.0

## 2. Final Release Objectives

The T16 final examination prepares the Community Services Management System for its v1.0.0 release.

The following objectives were completed:

| Objective | Result |
|---|---|
| Establish one authoritative application version | PASS |
| Update application version to 1.0.0 | PASS |
| Return application identity, status, and version through /health | PASS |
| Display v1.0.0 on the homepage | PASS |
| Add automated release version tests | PASS |
| Add cross-module integration testing | PASS |
| Complete two full regression runs | PASS |
| Complete manual acceptance testing | PASS |
| Prepare release documentation | PASS |

## 3. Files Changed

| File | Purpose |
|---|---|
| src/csms/config.py | Sets the authoritative application version to 1.0.0 |
| src/csms/templates/index.html | Displays the release version on the homepage |
| tests/test_smoke.py | Updates smoke tests for the v1.0.0 release |
| tests/test_release_version.py | Verifies the authoritative version, health endpoint, and homepage |
| tests/test_t16_release_integration.py | Tests resident registration, service request submission, persistence, and dashboard integration |
| docs/release-notes-v1.0.0.md | Documents the v1.0.0 release |
| docs/t16-final-checkpoint.md | Records the final examination results |

## 4. Cross-Module Integration Validation

The integration test verifies the following workflow:

1. Register a resident through the resident registration service.
2. Submit a service request for the registered resident.
3. Verify that the resident and service request are persisted in SQLite.
4. Retrieve the dashboard summary.
5. Verify that the dashboard reflects the registered resident and submitted request.

The test covers resident registration, service request submission, repository persistence, and dashboard reporting.

Result: PASS

## 5. Full Regression Testing

Command:

`.\.venv\Scripts\python.exe -m pytest`

| Run | Passed | Failed | Duration |
|---|---:|---:|---:|
| First full run | 181 | 0 | 92.12 seconds |
| Second full run | 181 | 0 | 86.55 seconds |

Both full regression runs completed successfully.

## 6. Manual Acceptance Testing

| Manual Check | Result | Notes |
|---|---|---|
| Application startup | PASS | Flask server started successfully |
| Homepage | PASS | Displayed v1.0.0 |
| Health endpoint | PASS | Returned the application identity |
| Health status | PASS | Returned ok |
| Health version | PASS | Returned 1.0.0 |

## 7. Repository and Release Documentation

- Release notes created in docs/release-notes-v1.0.0.md.
- Final checkpoint created in docs/t16-final-checkpoint.md.
- Existing T15 release readiness report preserved.
- Git whitespace validation completed using git diff --check with no errors.

## 8. Known Limitations

- Resident reactivation is outside the defined T16 scope.
- Production deployments must provide a strong CSMS_SECRET_KEY environment variable instead of relying on the development fallback secret.

## 9. Final Checkpoint Statement

READY FOR FINAL RELEASE REVIEW

The CSMS v1.0.0 implementation passed both full regression runs with 181 tests and no failures. The cross-module integration test, automated release version tests, and manual acceptance checks were successful.

The project is ready for the final pull request, merge, annotated version tag, and GitHub Release publication.
