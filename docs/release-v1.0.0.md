# CSMS v1.0.0
## Release Notes

## 1. Release Information

- Application: Community Services Management System
- Release Version: 1.0.0
- Release Tag: v1.0.0
- Technology Stack: Python 3.13, Flask 3.1, SQLite, pytest
- Repository: https://github.com/UPHSL/csms-python-jerstin-mane

## 2. Release Overview

CSMS v1.0.0 is the first final release of the Community Services Management System.

This release establishes the application's official version, verifies the health endpoint, displays the release version in the homepage, and validates the integration of important application features.

## 3. Release Changes

| Area | Changes |
|---|---|
| Application configuration | Updated the authoritative APP_VERSION value to 1.0.0 |
| Health endpoint | Returns application identity, operational status, and release version |
| Homepage | Displays the v1.0.0 release version |
| Release testing | Added automated tests for the application version and release display |
| Integration testing | Added a cross-module test for resident registration, service request submission, and dashboard summary |
| Regression testing | Completed two successful full test suite runs |

## 4. Automated Test Results

Command:

`.\.venv\Scripts\python.exe -m pytest`

| Test Run | Result | Duration |
|---|---:|---:|
| Run 1 | 181 passed, 0 failed | 92.12 seconds |
| Run 2 | 181 passed, 0 failed | 86.55 seconds |

Both full regression runs completed successfully.

## 5. Manual Verification

| Check | Result |
|---|---|
| Flask application starts successfully | PASS |
| Homepage displays v1.0.0 | PASS |
| Health endpoint returns application identity | PASS |
| Health endpoint returns status ok | PASS |
| Health endpoint returns version 1.0.0 | PASS |

## 6. Known Limitations

- Resident reactivation is not included in this release.
- The development configuration includes a fallback secret key. Production deployments must provide a strong secret through the CSMS_SECRET_KEY environment variable.

## 7. Release Statement

CSMS v1.0.0 passed its automated regression tests and manual release verification.

The application is ready for the final release process, including pull request review, merging, version tagging, and GitHub Release publication.
