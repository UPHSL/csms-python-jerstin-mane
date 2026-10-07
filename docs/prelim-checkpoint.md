# Preliminary Examination Checkpoint - T03

## Developer Information

Name: Jerstin M. Mane  
GitHub Username: jerstin-mane  
Primary Technology Stack: Python with Flask  
T03 Branch: feature/t03-resident-persistence  

## My T03 Implementation

I used Python and SQLite to save Resident information in a database file. The database is stored in `instance/csms.db`, while the tests use temporary database files. The `ResidentRepository` is responsible for saving and getting Resident information from the database. When `save()` is used, the Resident information is inserted into the `residents` table. SQLite automatically gives the Resident a unique ID, and `cursor.lastrowid` gets that ID and puts it in the Resident object. The `find_by_id()` method searches for a Resident using the ID and changes the database result back into a Resident object. If the ID does not exist, the method returns `None`.

## My Persistence Design Decision

I decided to put the database setup in `database.py` and the Resident database operations in `resident_repository.py`. I chose this because it keeps the database setup and Resident operations separate and easier to understand. I used `CREATE TABLE IF NOT EXISTS` so the database can be opened again without deleting the existing data. I also used a file-based database because T03 requires real data to be saved even after creating a new repository.

## Files I Changed

File: `src/csms/database.py`  
Purpose: Creates the SQLite database and the Resident table.

File: `src/csms/repositories/resident_repository.py`  
Purpose: Saves Residents and finds Residents by their ID.

File: `tests/test_resident_repository.py`  
Purpose: Tests if Residents can be saved, found, and kept correctly in the database.

File: `docs/prelim-checkpoint.md`  
Purpose: Contains my explanation of my T03 work, problems, and testing.

## Problem I Encountered

Problem or error: Flask could not start when I used `--app src.app`.

Cause: My project does not have an `app.py` file inside the `src` folder.

How I resolved it: I checked my project folders and found that the Flask application is inside the `csms` package. I changed the command to `python -m flask --app csms run`, and Flask started successfully. I also checked the main page and the `/health` page.

## My Student-Designed Test

Test name: `test_inactive_resident_status_is_preserved`

What it verifies: This test checks if an Inactive Resident can be saved and retrieved with the same Inactive status.

Why I chose this scenario: I chose this test because the Resident status is important information, and I wanted to make sure that Inactive Residents do not become Active when they are retrieved from the database.

## Tools and References Used

- Visual Studio Code for writing and editing my code.
- PowerShell for running my commands.
- Python and SQLite for saving Resident information.
- Flask for checking that the application still works.
- pytest for testing my code.
- Git and GitHub for managing my project.
- The T03 guide provided by our instructor for the requirements.
- ChatGPT as an AI coding assistant for helping me understand errors, project files, and T03 requirements.