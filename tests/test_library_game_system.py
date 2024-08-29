import pytest
import library
import hashlib



@pytest.fixture()
def app():
    app = library.create_app()
    salt = app.config["PASSWORD_SALT"]
    database = app.config["MONGODB_INST"]

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
    
    database.users.insert_one(admin)
    yield app
    database.users.delete_one(admin)


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
        response = client.post("/image/upload", data = body, headers = headers)
        filename = response.json.get("filename")
        yield filename
        database.images.delete_one({"filename": filename})


def test_game_system_create(app, db, client, image):
    assert True
    #client.post("/game-system/create")