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
| Update package metadata to 1.0.0 | PASS |
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
| pyproject.toml | Updates package metadata version to 1.0.0 |
| src/csms/config.py | Sets the authoritative application version to 1.0.0 |
| src/csms/templates/index.html | Displays the release version on the homepage |
| tests/test_smoke.py | Updates smoke tests for the v1.0.0 release |
| tests/test_release_version.py | Verifies the application version, health endpoint, and homepage |
| tests/test_t16_release_integration.py | Tests resident registration, service request submission, persistence, and dashboard integration |
| docs/release-v1.0.0.md | Documents the v1.0.0 release |
| docs/final-checkpoint.md | Records the final examination results |

## 4. Cross-Module Integration Validation

**Test Name:**

`test_resident_registration_request_submission_and_dashboard_integration`

The integration test verifies the following workflow:

1. Register a resident through the resident registration service.
2. Submit a service request for the registered resident.
3. Verify that the resident and service request are persisted in SQLite.
4. Retrieve the dashboard summary.
5. Verify that the dashboard reflects the registered resident and submitted request.

The test covers three main responsibilities: Resident Registration, Service Request Submission, and Dashboard Aggregation. It also verifies repository persistence and the final stored system state using a real SQLite database created for the test.

**Result: PASS**

## 5. Full Regression Testing

Command:

`.\.venv\Scripts\python.exe -m pytest`

| Run | Passed | Failed | Duration |
|---|---:|---:|---:|
| Final Regression Run 1 | 181 | 0 | 92.12 seconds |
| Final Regression Run 2 | 181 | 0 | 86.55 seconds |

Both full regression runs completed successfully with no failures.

## 6. Manual Acceptance Testing

| Manual Check | Result | Notes |
|---|---|---|
| Application startup | PASS | Flask server started successfully |
| Homepage | PASS | Displayed v1.0.0 |
| Health endpoint | PASS | Returned the application identity |
| Health status | PASS | Returned ok |
| Health version | PASS | Returned 1.0.0 |

The manual checks confirmed that the running application reported the correct release version.

## 7. Technical Decision

The application version is maintained in `BaseConfig.APP_VERSION` in `src/csms/config.py`. The health endpoint and homepage use the configured application version so that both display consistent release information.

The package metadata in `pyproject.toml` was also updated to 1.0.0 to match the application release.

## 8. Problem Encountered and Verification

During manual verification, the health endpoint initially returned the previous version, 0.1.0, even though the source code had already been updated.

The cause was an older Flask server process still running on the local machine. The old processes were stopped, and the application was restarted without the reloader. The health endpoint then correctly returned version 1.0.0.

This confirmed the importance of restarting the correct application process during release verification.

## 9. Repository and Release Documentation

- Release notes created in `docs/release-v1.0.0.md`.
- Final checkpoint created in `docs/final-checkpoint.md`.
- Existing T15 release readiness report preserved.
- Git whitespace validation completed using `git diff --check` with no errors.
- T16 changes committed and pushed to `feature/t16-final-release`.

## 10. Tools and References Used

- Python 3.13
- Flask 3.1
- SQLite
- pytest
- Visual Studio Code
- Windows PowerShell
- Git and GitHub
- Existing CSMS project modules, tests, and course requirements

## 11. Known Limitations

- Resident reactivation is outside the defined T16 scope.
- Production deployments must provide a strong `CSMS_SECRET_KEY` environment variable instead of relying on the development fallback secret.
- Authentication, role management, and other features outside the defined project scope are not included in this release.

## 12. Final Checkpoint Statement

**CSMS v1.0.0 - READY FOR RELEASE**

The CSMS v1.0.0 implementation passed both full regression runs with 181 tests and no failures. The cross-module integration test, automated release version tests, and manual acceptance checks were successful.

The project is ready for final pull request review, merge, annotated version tagging, and GitHub Release publication.