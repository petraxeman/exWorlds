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
    
    db.execute("DELETE FROM packs WHERE path = %s", ("game-system://test-game-system",))

    for i in range(10):
        db.execute("DELETE FROM packs WHERE path = %s", (f"game-system://test-game-system-{i}",))

#
# upload.py
#

def test_pack_upload(client, create_user):
    _, _, token = create_user("test-user", "-")
    
    headers = {"auth-token": token}
    body = {
        "name": "Test game system",
        "path": "game-system://test-game-system",
        "image-name": "image",
        }
    response = client.post("/api/packs/upload", headers = headers, json = body)
    
    assert response.status_code == 200


def test_pack_update(db, client, create_user):
    _, _, token = create_user("test-user", "-")
    
    headers = {"auth-token": token}
    body = {
        "name": "Test game system",
        "path": "game-system://test-game-system",
        "image-name": "image",
        }
    response = client.post("/api/packs/upload", headers = headers, json = body)
    
    body["name"] = "Test game system 2"
    response = client.post("/api/packs/upload", headers = headers, json = body)
    
    result_pack = db.fetchone("SELECT * FROM packs WHERE path = %s", ("game-system://test-game-system",))
    
    assert response.status_code == 200
    assert "hash" in response.json.keys()
    assert result_pack["name"] == "Test game system 2"


def test_pack_update_by_another_user(db, client, create_user):
    _, _, token_1 = create_user("test-user", "-")
    _, _, token_2 = create_user("another-user", "-")
    
    headers = {"auth-token": token_1}
    body = {
        "name": "Test game system",
        "path": "game-system://test-game-system",
        "image-name": "image",
        }
    response = client.post("/api/packs/upload", headers = headers, json = body)
    
    body["name"] = "Test game system 2"
    headers["auth-token"] = token_2
    response = client.post("/api/packs/upload", headers = headers, json = body)
    
    result_pack = db.fetchone("SELECT * FROM packs WHERE path = %s", ("game-system://test-game-system",))
    
    assert response.status_code == 401
    assert response.json["msg"] == "You can't do that."
    assert result_pack["name"] == "Test game system"


def test_pack_update_by_server_admin(db, client, create_user):
    _, _, token_1 = create_user("test-user", "-")
    _, _, token_2 = create_user("test-admin", "-", ["server-admin"])
    
    headers = {"auth-token": token_1}
    body = {
        "name": "Test game system",
        "path": "game-system://test-game-system",
        "image-name": "image",
        }
    response = client.post("/api/packs/upload", headers = headers, json = body)
    
    body["name"] = "Test game system 2"
    headers["auth-token"] = token_2
    response = client.post("/api/packs/upload", headers = headers, json = body)
    
    result_pack = db.fetchone("SELECT * FROM packs WHERE path = %s", ("game-system://test-game-system",))
    
    assert response.status_code == 200
    assert "hash" in response.json.keys()
    assert result_pack["name"] == "Test game system 2"


#
# handlers.py
#

def test_toggle_hidden(db, client, create_user):
    _, _, token_1 = create_user("test-user", "test-passwd")
    
    body = {
        "name": "Test game system",
        "path": "game-system://test-game-system",
        "image-name": "image",
        }
    response = client.post("/api/packs/upload", headers = {"auth-token": token_1}, json = body)

    response = client.post("/api/packs/toggle/hide", headers = {"auth-token": token_1}, json = {"path": "game-system://test-game-system"})
    
    new_pack = db.fetchone("SELECT * FROM packs WHERE path = 'game-system://test-game-system'")

    assert response.status_code == 200
    assert new_pack["hidden"]
    
    _, _, token_2 = create_user("another-user", "test-passwd")
    response = client.post(
        "/api/packs/toggle/hide",
        headers = {"auth-token": token_2},
        json = {"path": "game-system://test-game-system"}
        )

    new_pack = db.fetchone("SELECT * FROM packs WHERE path = 'game-system://test-game-system'")
    assert response.status_code == 401
    assert new_pack["hidden"]


def test_toggle_freezed(db, client, create_user):
    _, _, token_1 = create_user("test-user", "test-passwd")
    
    body = {
        "name": "Test game system",
        "path": "game-system://test-game-system",
        "image-name": "image",
        }
    response = client.post("/api/packs/upload", headers = {"auth-token": token_1}, json = body)
    response = client.post(
        "/api/packs/toggle/freeze",
        headers = {"auth-token": token_1},
        json = {"path": "game-system://test-game-system"}
        )
    
    new_pack = db.fetchone("SELECT * FROM packs WHERE path = 'game-system://test-game-system'")

    assert response.status_code == 200
    assert new_pack["freezed"]
    
    _, _, token_2 = create_user("another-user", "test-passwd")
    response = client.post(
        "/api/packs/toggle/freeze",
        headers = {"auth-token": token_2},
        json = {"path": "game-system://test-game-system"}
        )

    new_pack = db.fetchone("SELECT * FROM packs WHERE path = 'game-system://test-game-system'")
    assert response.status_code == 401
    assert new_pack["freezed"]


def test_get_pack(client, create_user):
    _, _, token_1 = create_user("test-user", "test-passwd")
    
    body = {
        "name": "Test game system",
        "path": "game-system://test-game-system",
        "image-name": "image",
        }
    response = client.post("/api/packs/upload", headers = {"auth-token": token_1}, json = body)
    response = client.post("/api/packs/toggle/hide", headers = {"auth-token": token_1}, json = {"path": "game-system://test-game-system"})
    response = client.post("/api/packs/get", headers = {"auth-token": token_1}, json = {"path-list": ["game-system://test-game-system"]})
    
    assert response.status_code == 200
    assert len(response.json["packs"]) == 1
    
    _, _, token_2 = create_user("another-user", "test-passwd")
    response = client.post("/api/packs/get", headers = {"auth-token": token_2}, json = {"path-list": ["game-system://test-game-system"]})
    
    assert response.status_code == 401


def test_get_pack_hash(client, create_user):
    _, _, token_1 = create_user("test-user", "test-passwd")
    
    body = {
        "name": "Test game system",
        "path": "game-system://test-game-system",
        "image-name": "image",
        }
    response = client.post("/api/packs/upload", headers = {"auth-token": token_1}, json = body)
    response = client.post("/api/packs/toggle/hide", headers = {"auth-token": token_1}, json = {"path": "game-system://test-game-system"})
    response = client.post("/api/packs/get-hash", headers = {"auth-token": token_1}, json = {"path-list": ["game-system://test-game-system"]})
    
    assert response.status_code == 200
    assert len(response.json["hashes"]) == 1
    
    _, _, token_2 = create_user("another-user", "test-passwd")
    response = client.post("/api/packs/get-hash", headers = {"auth-token": token_2}, json = {"path-list": ["game-system://test-game-system"]})
    
    assert response.status_code == 401


#
# get_by_page.py
#

def test_get_by_page(db, client, create_user):
    _, _, token_1 = create_user("test-user", "test-passwd")
    
    for i in range(10):
        body = {
            "name": f"Test game system at number {i}",
            "path": f"game-system://test-game-system-{i}",
            "image-name": "image",
        }
        client.post("/api/packs/upload", headers = {"auth-token": token_1}, json = body)
    
    for i in [7, 8, 9]:
        client.post(
            "/api/packs/toggle/favorite",
            headers = {"auth-token": token_1},
            json = {"path": f"game-system://test-game-system-{i}"}
            )

    for i in [4, 5, 6]:
        client.post(
            "/api/packs/toggle/like",
            headers = {"auth-token": token_1},
            json = {"path": f"game-system://test-game-system-{i}"}
            )

    client.post(
            "/api/packs/toggle/hide",
            headers = {"auth-token": token_1},
            json = {"path": f"game-system://test-game-system-3"}
            )
    
    response = client.post("/api/pack/get-by-page", headers = {"auth-token": token_1}, json = {"page": 1})
    
    assert len(response.json["paths"]) == 10
    assert response.json["paths"][0]["path"] in ["game-system://test-game-system-7", "game-system://test-game-system-8", "game-system://test-game-system-9"]
    assert response.json["paths"][3]["path"] in ["game-system://test-game-system-4", "game-system://test-game-system-5", "game-system://test-game-system-6"]

    
    _, _, token_2 = create_user("another-user", "test-passwd")
    
    response = client.post("/api/pack/get-by-page", headers = {"auth-token": token_2}, json = {"page": 1, "search": "1"})
        
    assert len(response.json["paths"]) == 9
    assert response.json["paths"][0]["path"] == "game-system://test-game-system-1"