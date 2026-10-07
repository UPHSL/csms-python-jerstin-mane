# Midterm Checkpoint — T10

## 1. Developer Information

- **Name:** Jerstin M. Mane
- **GitHub Username:** jerstin-mane
- **Stack:** Python, Flask, SQLite, pytest
- **T10 Branch:** `feature/t10-service-request-status`

## 2. My T10 Implementation

For T10, I added service request status management to the existing CSMS project. I created a status result class to handle success, not found, unsupported status, and invalid transition results. I also added an `update_status()` method to the existing Service Request repository for updating the persisted status. The status service checks the current request before allowing a status change. It only updates the database when the requested transition is valid. The implementation keeps the existing request ID, resident ID, service type, description, and date requested unchanged. I also created tests for the required status transitions and other invalid cases.

## 3. My Transition Rules

The allowed service request transitions are:

- `Pending → In Progress`
- `Pending → Cancelled`
- `In Progress → Completed`
- `In Progress → Cancelled`

The following transitions are rejected:

- `Pending → Completed`
- `In Progress → Pending`
- `Completed → any other status`
- `Cancelled → any other status`
- Same status to the same status
- Unsupported statuses such as `Approved`

Completed and Cancelled are terminal statuses.

## 4. Files I Changed

- `src/csms/repositories/service_request_repository.py` — Added `update_status()` to update the persisted service request status.
- `src/csms/services/service_request_status_result.py` — Added result handling for successful and failed status updates.
- `src/csms/services/service_request_status_service.py` — Added the T10 status management and transition rules.
- `tests/test_service_request_status.py` — Added tests for valid transitions, invalid transitions, terminal statuses, unsupported statuses, not found requests, field preservation, and persistence.

## 5. Problem I Encountered

One problem I needed to consider was making sure invalid transitions did not change the request in the database. I checked the T10 requirements and separated the transition checking from the repository update. The service checks the current status and target status first. The repository update is only called when the transition is valid. I tested invalid transitions and confirmed that the original status remains unchanged.

## 6. Student-Designed Test

**Test Name:** `test_valid_status_transition_persists_across_repository_instances`

This test verifies that a valid status update is actually saved in the database and can still be retrieved using a separate repository instance. I chose this test to make sure the status change is not only correct in memory but is also properly persisted.

## 7. Tools and References Used

- Python 3.13.15
- Flask
- SQLite
- pytest
- Git and GitHub
- Visual Studio Code / Notepad
- T10 official activity guide
- Existing T01–T09 project code and tests
- ChatGPT was used as an AI assistant for guidance, code planning, and debugging.