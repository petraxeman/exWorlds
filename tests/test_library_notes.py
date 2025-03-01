import pytest
import library
import hashlib
import jwt
import datetime



@pytest.fixture(scope="session")
def app():
    app = library.create_app()
    yield app


@pytest.fixture(scope="session")
def db(app):
    return app.extensions["postgresdb"]


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def create_user(db, app):
    created_users = []
    
    def _create_user(username: str, password: str, rights: list = ['any-create']):
        password_hash = hashlib.pbkdf2_hmac("sha512", str(password).encode(), str(app.config['PASSWORD_SALT']).encode(), 2 ** 8).hex()
        expire_data = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
        token = jwt.encode({"username": username, "expire_date": expire_data}, key = app.config["JWT_SECRET"], algorithm="HS256")
        db.execute("INSERT INTO users (username, password_hash, rights) VALUES (%s, %s, %s)", (username, password_hash, rights,))
        
        created_users.append(username)
        
        return username, password_hash, token
    
    yield _create_user

    for username in created_users:
        db.execute("DELETE FROM users WHERE username = %s", (username,))


@pytest.fixture(autouse=True)
def run_after(db):
    clear_db(db)
    yield
    clear_db(db)


@pytest.fixture(scope="session", autouse=True)
def run_after_all(db):
    yield
    clear_db(db)


def clear_db(_db):
    _db.execute("DELETE FROM users WHERE username = 'test-user'")
    _db.execute("DELETE FROM users WHERE username = 'test-admin'")
    _db.execute("DELETE FROM users WHERE username = 'another-user'")
    
    _db.execute("DELETE FROM packs WHERE path = %s", ("gc:test-game-system",))
    _db.execute("DELETE FROM tables WHERE path = %s", ("gc:test-game-system.rules",))
    _db.execute("DELETE FROM tables WHERE path = %s", ("gc:test-game-system.macros",))
    
    _db.execute("DELETE FROM packs WHERE path = %s", ("gc:game-system",))
    
    for i in range(10):
        _db.execute("DELETE FROM packs WHERE path = %s", (f"gc:test-game-system-{i}",))
        _db.execute("DELETE FROM tables WHERE path = %s", (f"gc:test-game-system-{i}.rules",))
        _db.execute("DELETE FROM tables WHERE path = %s", (f"gc:test-game-system-{i}.macros",))
    
    _db.execute("DELETE FROM notes WHERE starts_with(path, %s)", ("gc:test-game-system.",))


def init_workspace(c, u):

    body = {
        "name": "Test game system",
        "path": "gc:test-game-system",
        "image-name": "image",
        }
    
    c.post("/api/packs/upload", headers = {"auth-token": u}, json = body)
    
    body = {
        "name": "Test table",
        "path": "gc:test-game-system.test-table",
        "common": {
            "search-fields": ["name"],
            "short-view": ["name"],
            "table-icon": "opened-book",
            "table-display": "list",
        },
        "data": {
            "properties": {},
            "macros": {},
            "schema": [[{"codename": "codename"}, {"codename": "name"}, {"codename": "damage"}, {"codename": "is-work"}]],
            "fields": {
                "codename": {"type": "text", "name": "Codename"},
                "name": {"type": "text", "name": "Name"},
                "damage": {"type": "integer", "name": "Damage"},
                "damage-dices": {"type": "dice", "name": "Damage dices"},
                "is-work": {"type": "boolean", "name": "Is work"}
            }
        }
    }
    
    c.post("/api/tables/upload", headers = {"auth-token": u}, json = body)


def test_note_upload(db, client, create_user):
    _, _, token = create_user("test-user", "test-password")

    init_workspace(client, token)
    
    data = {"path": "gc:test-game-system.test-table.test-note", "fields": {"codename": "Heroine", "name": "Heroine in heroine", "damage": 100, "is-work": True}}
    
    response = client.post("/api/notes/upload", headers = {"auth-token": token}, json = data)
    
    assert response.status_code == 200
    assert db.fetchall("SELECT * FROM notes WHERE path = 'gc:test-game-system.test-table.test-note';")


def test_note_delete(client, create_user):
    _, _, token = create_user("test-user", "test-password")

    init_workspace(client, token)
    
    data = {"path": "gc:test-game-system.test-table.test-note", "fields": {"codename": "Heroine", "name": "Heroine in heroine", "damage": 100, "is-work": True}}
    
    client.post("/api/notes/upload", headers = {"auth-token": token}, json = data)
    
    response = client.post("/api/notes/delete", headers = {"auth-token": token}, json = {"path": "gc:test-game-system.test-table.test-note"})

    assert response.status_code == 200


def test_note_get_by_path(client, create_user):
    _, _, token = create_user("test-user", "test-password")

    init_workspace(client, token)
    
    data = {"path": "gc:test-game-system.test-table.test-note", "fields": {"codename": "Heroine", "name": "Heroine in heroine", "damage": 100, "is-work": True}}
    
    client.post("/api/notes/upload", headers = {"auth-token": token}, json = data)
    
    response = client.post("/api/notes/get", headers = {"auth-token": token}, json = {"path-list": ["gc:test-game-system.test-table.test-note"]})

    assert response.status_code == 200


def test_note_get_by_query(db, client, create_user):
    _, _, token = create_user("test-user", "test-password")

    init_workspace(client, token)
    
    data = {
        "path": "gc:test-game-system.test-table.test-note",
        "fields": {
            "codename": "Heroine",
            "name": "Heroine in heroine",
            "damage": 100, 
            "is-work": True,
            "damage-dices": "1d20"
            }
        }
    
    client.post("/api/notes/upload", headers = {"auth-token": token}, json = data)

    data = {
        "common": {
            "page": 1,
            "source": "gc:test-game-system.test-table"
        },
        "filters": [
            {"codename": "damage", "check": "avg", "min": 10, "max": 1000}
        ]
    }
    
    response = client.post("/api/notes/search", headers = {"auth-token": token}, json = data)

    assert response.status_code == 200