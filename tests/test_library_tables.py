import pytest
import library
import hashlib
import jwt
import datetime



@pytest.fixture()
def app():
    app = library.create_app()
    yield app


@pytest.fixture()
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
        db.execute("INSERT INTO users (username, password_hash, rights) VALUES (%s, %s, %s)", (username, password_hash, rights))
        
        created_users.append(username)
        
        return username, password_hash, token
    
    yield _create_user

    for username in created_users:
        db.execute("DELETE FROM users WHERE username = %s", (username,))


@pytest.fixture(autouse=True)
def run_after(db):
    yield
    db.execute("DELETE FROM users WHERE username = 'test-user'")
    db.execute("DELETE FROM users WHERE username = 'test-admin'")
    db.execute("DELETE FROM users WHERE username = 'another-user'")
    
    db.execute("DELETE FROM packs WHERE path = %s", ("gc:test-game-system",))

    db.execute("DELETE FROM tables WHERE path = 'gc:test-game-system.test-table'")
    db.execute("DELETE FROM tables WHERE path = 'gc:test-game-system.rules'")
    db.execute("DELETE FROM tables WHERE path = 'gc:test-game-system.macros'")
    

def insert_table(db, username):
    user = db.fetchone("SELECT * FROM users WHERE username = %s", (username,))
    table = {
        "name": "Test table",
        "owner": user["uid"],
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
            "schema": [{"codename": "codename"}, {"codename": "name"}],
            "fields": {
                "codename": {"type": "text", "name": "Codename"},
                "name": {"type": "text", "name": "Name"}
            }
        },
        "hash": "xxx"
    }
    db.execute("INSERT INTO tables (name, path, owner, common, data, hash) VALUES (%(name)s, %(path)s, %(owner)s, %(common)s, %(data)s, %(hash)s)", table)



def test_table_upload(db, client, create_user):
    _, _, token = create_user("test-user", "test-passwd")
    
    body = {
        "name": "Test game system",
        "path": "gc:test-game-system",
        "image-name": "image",
    }
    client.post("/api/packs/upload", headers = {"auth-token": token}, json = body)
    
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
            "schema": [{"codename": "codename"}, {"codename": "name"}],
            "fields": {
                "codename": {"type": "text", "name": "Codename"},
                "name": {"type": "text", "name": "Name"}
            }
        }
    }
    
    response = client.post("/api/tables/upload", headers = {"auth-token": token}, json = body)

    table = db.fetchone("SELECT * FROM tables WHERE path = 'gc:test-game-system.test-table'")

    assert response.status_code == 200
    assert table


def test_table_get(db, client, create_user):
    username, _, token = create_user("test-user", "test-passwd")
    
    body = {
        "name": f"Test game system",
        "path": f"gc:test-game-system",
        "image-name": "image",
    }
    
    client.post("/api/packs/upload", headers = {"auth-token": token}, json = body)
    
    insert_table(db, username)
    
    response = client.post("/api/tables/get", headers = {"auth-token": token}, json = {"path-list": ["gc:test-game-system.test-table"]})
    
    assert response.status_code == 200


def test_table_get_hash(db, client, create_user):
    username, _, token = create_user("test-user", "test-passwd")
    
    body = {
        "name": f"Test game system",
        "path": f"gc:test-game-system",
        "image-name": "image",
    }
    client.post("/api/packs/upload", headers = {"auth-token": token}, json = body)
    
    insert_table(db, username)
    
    response = client.post("/api/tables/get-hash", headers = {"auth-token": token}, json = {"path-list": ["gc:test-game-system.test-table"]})
    
    assert response.status_code == 200


def test_table_get_by_pack(db, client, create_user):
    username, _, token = create_user("test-user", "test-passwd")
    
    body = {
        "name": f"Test game system",
        "path": f"gc:test-game-system",
        "image-name": "image",
    }
    client.post("/api/packs/upload", headers = {"auth-token": token}, json = body)
    
    insert_table(db, username)
    
    response = client.post("/api/tables/get-by-pack", headers = {"auth-token": token}, json = {"path": "gc:test-game-system"})
    
    assert response.status_code == 200