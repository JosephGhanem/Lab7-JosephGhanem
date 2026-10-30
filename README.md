# Lab 7 - Python Testing

Joseph Ghanem — Software Tools Lab, Fall 2026–2027.

This project extends [my Lab 5 Flask/SQLite app](https://github.com/JosephGhanem/Lab5-JosephGhanem) with pytest coverage for all ten graded activities. The test file is `test_user_Joseph_Ghanem.py`.

## Setup and test

Requires Python 3.9 or newer. From this project directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -v
```

Run the application with `python app.py`. The API listens at `http://localhost:5000`. Set `PORT=5001` if that port is occupied. The database is created automatically beside `database.py`, or at the path specified by `DATABASE_PATH`.

## Initial users

Lab 5 originally initialized an empty table. Lab 7 requires checking specified users at first launch; this version specifies the following sample data. These are project sample records, not a user list supplied by the Lab 7 handout.

| ID | Name | Email | Phone | Address | Country |
| --- | --- | --- | --- | --- | --- |
| 1 | Joseph Ghanem | jhg06@mail.aub.edu | 01000001 | Beirut | Lebanon |
| 2 | John Doe | john@example.com | 01000002 | Innsbruck | Austria |
| 3 | Jane Doe | jane@example.com | 01000003 | Paris | France |

The app creates and seeds the table in a single transaction only when the table does not exist. Restarting does not duplicate, restore deleted users, or overwrite updated users. An existing Lab 5 database is preserved. Start with a new database path to see the initial records.

## Graded coverage

| Activity | Test |
| --- | --- |
| Database creation and specified initial users | `test_database_created_with_specified_users_on_first_run` |
| Insert_user | `test_insert_user` |
| Get_users | `test_get_users` |
| Get_users_by_id | `test_get_users_by_id` (Lab 5 function: `get_user_by_id`) |
| Update_user | `test_update_user` |
| Delete_user | `test_delete_user` |
| Api_get_user | `test_api_get_user` and `test_api_get_users` |
| Api_add_user | `test_api_add_user` |
| Api_update_user | `test_api_update_user` |
| Api_delete_user | `test_api_delete_user` |

Additional tests cover persistence across restarts, missing users, invalid input, partial updates, and SQL-like strings. Fixtures give each test its own temporary SQLite database. API tests use Flask's test client to run the actual handlers and database operations, without mocks or a separately running server. They check HTTP status, complete response data, and persisted writes/deletions. These tests do not establish network deployment behavior.

## API

| Method | Path | Success |
| --- | --- | --- |
| GET | `/api/users` | 200 |
| GET | `/api/users/<id>` | 200 |
| POST | `/api/users/add` | 201 |
| PUT | `/api/users/update` | 200 |
| PATCH | `/api/users/<id>` | 200 |
| DELETE | `/api/users/delete/<id>` | 200 |

POST/PUT use JSON fields `name`, `email`, `phone`, `address`, `country`; PUT also requires integer `user_id`. Missing users return 404, invalid fields return 400, and non-JSON bodies return 415.

## Evidence and submission

`evidence/pytest-results.txt` records the actual pytest run. `evidence/test-results.png` is an image rendered from that captured output, rather than a screenshot of a terminal window. The ZIP includes all source, dependencies, tests, and evidence; virtual environments and generated databases are excluded.

Verification: 28 tests passed with pytest 8.4.2 on Python 3.9.6 (exit code 0). See the captured output and JUnit report in `evidence/`.
