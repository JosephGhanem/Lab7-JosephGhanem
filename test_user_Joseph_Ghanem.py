"""Lab 7 graded tests: SQLite CRUD and real Flask request handlers."""
import sqlite3

import pytest

import database as db
from app import create_app


EXPECTED_USERS = [
    dict(user_id=1, name="Joseph Ghanem", email="jhg06@mail.aub.edu", phone="01000001", address="Beirut", country="Lebanon"),
    dict(user_id=2, name="John Doe", email="john@example.com", phone="01000002", address="Innsbruck", country="Austria"),
    dict(user_id=3, name="Jane Doe", email="jane@example.com", phone="01000003", address="Paris", country="France"),
]


@pytest.fixture
def database_path(tmp_path):
    """A fresh file for each test; never touch the application database."""
    return tmp_path / "users.db"


@pytest.fixture
def app(database_path):
    application = create_app(database_path)
    application.config.update(TESTING=True)
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seeded_db(app, database_path):
    return database_path


@pytest.fixture
def user():
    return dict(name="Test Student", email="student@example.com", phone="03123456", address="Hamra, Beirut", country="Lebanon")


def test_database_created_with_specified_users_on_first_run(database_path):
    assert not database_path.exists()
    create_app(database_path)
    assert database_path.is_file()
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT * FROM users ORDER BY user_id").fetchall()
    assert [dict(row) for row in rows] == EXPECTED_USERS


def test_startup_preserves_updates_without_duplicate_seeds(seeded_db):
    updated = dict(EXPECTED_USERS[0], name="Updated Joseph")
    db.update_user(updated, seeded_db)
    create_app(seeded_db)
    assert db.get_users(seeded_db) == [updated, *EXPECTED_USERS[1:]]


def test_restart_does_not_restore_deleted_users(seeded_db):
    for expected in EXPECTED_USERS:
        assert db.delete_user(expected["user_id"], seeded_db)
    create_app(seeded_db)
    assert db.get_users(seeded_db) == []


def test_insert_user(seeded_db, user):
    inserted = db.insert_user(user, seeded_db)
    assert inserted == dict(user, user_id=4)
    assert db.get_user_by_id(4, seeded_db) == inserted
    assert len(db.get_users(seeded_db)) == 4


def test_get_users(seeded_db):
    assert db.get_users(seeded_db) == EXPECTED_USERS


def test_get_users_by_id(seeded_db):
    assert db.get_user_by_id(2, seeded_db) == EXPECTED_USERS[1]


def test_get_users_by_id_missing(seeded_db):
    assert db.get_user_by_id(9999, seeded_db) is None


def test_update_user(seeded_db, user):
    updated = dict(user, user_id=2)
    assert db.update_user(updated, seeded_db) == updated
    assert db.get_user_by_id(2, seeded_db) == updated
    assert db.get_user_by_id(1, seeded_db) == EXPECTED_USERS[0]
    assert len(db.get_users(seeded_db)) == 3


def test_update_user_missing(seeded_db, user):
    assert db.update_user(dict(user, user_id=9999), seeded_db) is None
    assert db.get_users(seeded_db) == EXPECTED_USERS


def test_delete_user(seeded_db):
    assert db.delete_user(2, seeded_db) is True
    assert db.get_user_by_id(2, seeded_db) is None
    assert db.get_users(seeded_db) == [EXPECTED_USERS[0], EXPECTED_USERS[2]]


def test_delete_user_missing(seeded_db):
    assert db.delete_user(9999, seeded_db) is False
    assert db.get_users(seeded_db) == EXPECTED_USERS


def test_api_get_users(client):
    response = client.get("/api/users")
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == EXPECTED_USERS


def test_api_get_user(client):
    response = client.get("/api/users/2")
    assert response.status_code == 200
    assert response.get_json() == EXPECTED_USERS[1]


def test_api_get_user_missing(client):
    response = client.get("/api/users/9999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found."}


def test_api_add_user(client, database_path, user):
    response = client.post("/api/users/add", json=user)
    assert response.status_code == 201
    expected = dict(user, user_id=4)
    assert response.get_json() == expected
    assert db.get_user_by_id(4, database_path) == expected
    downloaded = client.get("/api/users/4")
    assert downloaded.status_code == 200
    assert downloaded.get_json() == expected


def test_api_update_user(client, database_path, user):
    expected = dict(user, user_id=2)
    response = client.put("/api/users/update", json=expected)
    assert response.status_code == 200
    assert response.get_json() == expected
    assert db.get_user_by_id(2, database_path) == expected
    downloaded = client.get("/api/users/2")
    assert downloaded.status_code == 200
    assert downloaded.get_json() == expected
    assert db.get_user_by_id(1, database_path) == EXPECTED_USERS[0]


def test_api_update_user_missing(client, database_path, user):
    response = client.put("/api/users/update", json=dict(user, user_id=9999))
    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found."}
    assert db.get_users(database_path) == EXPECTED_USERS


def test_api_delete_user(client, database_path):
    response = client.delete("/api/users/delete/2")
    assert response.status_code == 200
    assert response.get_json() == {"status": "User deleted successfully"}
    assert db.get_user_by_id(2, database_path) is None
    downloaded = client.get("/api/users/2")
    assert downloaded.status_code == 404
    assert downloaded.get_json() == {"error": "User not found."}
    remaining = client.get("/api/users")
    assert remaining.status_code == 200
    assert remaining.get_json() == [EXPECTED_USERS[0], EXPECTED_USERS[2]]


def test_api_delete_user_missing(client, database_path):
    response = client.delete("/api/users/delete/9999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found."}
    assert db.get_users(database_path) == EXPECTED_USERS


@pytest.mark.parametrize("field", db.FIELDS)
def test_api_add_rejects_missing_fields(client, database_path, user, field):
    del user[field]
    response = client.post("/api/users/add", json=user)
    assert response.status_code == 400
    assert response.get_json() == {"error": f"{field} must be a nonempty string."}
    assert db.get_users(database_path) == EXPECTED_USERS


def test_api_update_rejects_invalid_id(client, database_path, user):
    response = client.put("/api/users/update", json=dict(user, user_id="2"))
    assert response.status_code == 400
    assert response.get_json() == {"error": "user_id must be a positive integer."}
    assert db.get_users(database_path) == EXPECTED_USERS


def test_api_add_rejects_non_json(client, database_path):
    response = client.post("/api/users/add", data="not JSON", content_type="text/plain")
    assert response.status_code == 415
    assert isinstance(response.get_json()["error"], str)
    assert db.get_users(database_path) == EXPECTED_USERS


def test_api_patch_preserves_other_fields(client, database_path):
    response = client.patch("/api/users/2", json={"address": "Beirut"})
    expected = dict(EXPECTED_USERS[1], address="Beirut")
    assert response.status_code == 200
    assert response.get_json() == expected
    assert db.get_user_by_id(2, database_path) == expected


def test_insert_handles_apostrophes_and_sql_text(seeded_db, user):
    user["name"] = "O'Neil'; DROP TABLE users; --"
    inserted = db.insert_user(user, seeded_db)
    assert db.get_user_by_id(inserted["user_id"], seeded_db) == inserted
    assert len(db.get_users(seeded_db)) == 4
