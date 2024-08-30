import pytest
import library
import hashlib



@pytest.fixture()
def app():
    app = library.create_app()
    salt = app.config["PASSWORD_SALT"]
    admin = {
            "username": "test-admin",
            "password-hash": hashlib.pbkdf2_hmac("sha512", "test-passwd".encode(), str(salt).encode(), 2 ** 8).hex(),
            "role": "admin",
            "waiting": {
                "registration": False,
                "approval": False
                },
            "black-list": [],
        }
    app.config["MONGODB_INST"].users.insert_one(admin)
    yield app
    app.config["MONGODB_INST"].users.delete_one(admin)


@pytest.fixture()
def db(app):
    return app.config["MONGODB_INST"]

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture()
def image(app, client):
    database = app.config["MONGODB_INST"]
    token = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    with open("placeholder.png", "rb") as image:
        body = "\r\n--ImageBoundary\r\n".encode()
        body += "Content-Disposition: form-data; name=\"image\"; filename=\"picture.webp\"\r\n".encode()
        body += "Content-Type: image/webp\r\n\r\n".encode()
        body += image.read()
        body += "\r\n--ImageBoundary--\r\n".encode()
        headers = {"Content-Type": "multipart/form-data; boundary=ImageBoundary", "auth-token": token}
        response = client.post("/api/image/upload", data = body, headers = headers)
        filename = response.json.get("filename")
        yield filename
        database.images.delete_one({"name": filename})

@pytest.fixture()
def second_user(app):
    salt = app.config["PASSWORD_SALT"]
    test_user = {
            "username": "test-user",
            "password-hash": hashlib.pbkdf2_hmac("sha512", "test-passwd".encode(), str(salt).encode(), 2 ** 8).hex(),
            "role": "user",
            "waiting": {
                "registration": False,
                "approval": False
                },
            "black-list": [],
        }
    app.config["MONGODB_INST"].users.insert_one(test_user)
    yield test_user
    app.config["MONGODB_INST"].users.delete_one(test_user)



def test_game_system_create_by_admin(db, client, image):
    admin = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    body = {"name": "Game system", "codename": "game-system", "image-name": image}
    response = client.post("/game-system/upload", headers = {"auth-token": admin}, json = body)
    assert response.status_code == 200
    assert response.json["hash"]
    assert db.structs.find_one({"type": "game-system", "codename": "game-system"})
    db.structs.delete_one({"codename": "game-system", "type": "game-system"})


def test_game_system_create_by_user(db, client, image, second_user):
    user = client.post("/api/login", json = {"username": "test-user", "password": "test-passwd"}).json.get("token")
    body = {"name": "Game system", "codename": "game-system", "image-name": image}
    response = client.post("/game-system/upload", headers = {"auth-token": user}, json = body)
    assert response.status_code == 200
    assert response.json["hash"]
    assert db.structs.find_one({"type": "game-system", "codename": "game-system"})
    db.structs.delete_one({"codename": "game-system", "type": "game-system"})


def test_double_creating_game_system(db, client, image, second_user):
    admin = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    user = client.post("/api/login", json = {"username": "test-user", "password": "test-passwd"}).json.get("token")
    body = {"name": "Game system", "codename": "game-system", "image-name": image}
    client.post("/game-system/upload", headers = {"auth-token": admin}, json = body)
    response = client.post("/game-system/upload", headers = {"auth-token": user}, json = body)
    assert response.status_code != 200
    db.structs.delete_one({"codename": "game-system", "type": "game-system"})


def test_changing_game_system(db, client, image):
    token = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    body = {"name": "Game system 1", "codename": "game-system", "image-name": image}
    response = client.post("/game-system/upload", headers = {"auth-token": token}, json = body)
    assert response.status_code == 200
    assert db.structs.find_one({"codename": "game-system", "type": "game-system"}).get("name") == "Game system 1"
    body["name"] = "Game system 2"
    response = client.post("/game-system/upload", headers = {"auth-token": token}, json = body)
    assert response.status_code == 200
    assert db.structs.find_one({"codename": "game-system", "type": "game-system"}).get("name") == "Game system 2"
    db.structs.delete_one({"codename": "game-system", "type": "game-system"})


def test_changing_user_game_system_by_admin(db, client, image, second_user):
    admin = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    user = client.post("/api/login", json = {"username": "test-user", "password": "test-passwd"}).json.get("token")
    body = {"name": "Game system 1", "codename": "game-system", "image-name": image}
    response = client.post("/game-system/upload", headers = {"auth-token": user}, json = body)
    assert response.status_code == 200
    body["name"] = "Game system 2"
    response = client.post("/game-system/upload", headers = {"auth-token": admin}, json = body)
    assert response.status_code == 200
    db.structs.delete_one({"codename": "game-system", "type": "game-system"})


def test_getting_game_system(db, client, image):
    admin = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    body = {"name": "Game system", "codename": "game-system", "image-name": image}
    client.post("/game-system/upload", headers = {"auth-token": admin}, json = body)
    response = client.post("/game-system/get", headers = {"auth-token": admin}, json = {"codename": "game-system"})
    assert response.status_code == 200
    db.structs.delete_one({"codename": "game-system", "type": "game-system"})


def test_getting_game_system_wrong(db, client, image):
    admin = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    body = {"name": "Game system", "codename": "game-system", "image-name": image}
    client.post("/game-system/upload", headers = {"auth-token": admin}, json = body)
    response = client.post("/game-system/get", json = {"codename": "game-system"})
    assert response.status_code != 200
    db.structs.delete_one({"codename": "game-system", "type": "game-system"})


def test_getting_game_system_hash(db, client, image):
    admin = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    body = {"name": "Game system", "codename": "game-system", "image-name": image}
    client.post("/game-system/upload", headers = {"auth-token": admin}, json = body)
    response = client.post("/game-system/get-hash", headers = {"auth-token": admin}, json = {"codename": "game-system"})
    assert response.status_code == 200
    assert response.json["hash"]
    db.structs.delete_one({"codename": "game-system", "type": "game-system"})


def test_getting_game_system_by_pages(db, client, image):
    admin = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    body = {"name": "Game system", "codename": "game-system", "image-name": image}
    client.post("/game-system/upload", headers = {"auth-token": admin}, json = body)
    response = client.post("/game-system/get-systems-by-page", headers = {"auth-token": admin}, json = {"page": "1"})
    assert response.status_code == 200
    assert response.json["systems"]
    db.structs.delete_one({"codename": "game-system", "type": "game-system"})


def test_getting_game_system_get_count(db, client, image):
    admin = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    body = {"name": "Game system", "codename": "game-system", "image-name": image}
    client.post("/game-system/upload", headers = {"auth-token": admin}, json = body)
    response = client.post("/game-systems/get-count", headers = {"auth-token": admin}, json = {"page": "1"})
    assert response.status_code == 200
    assert response.json["count"]
    db.structs.delete_one({"codename": "game-system", "type": "game-system"})



def test_getting_game_system_delete(db, client, image):
    admin = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    body = {"name": "Game system", "codename": "game-system", "image-name": image}
    client.post("/game-system/upload", headers = {"auth-token": admin}, json = body)
    response = client.post("/game-systems/delete", headers = {"auth-token": admin}, json = {"codename": "game-system"})
    assert response.status_code == 200
    db.structs.delete_one({"codename": "game-system", "type": "game-system"})