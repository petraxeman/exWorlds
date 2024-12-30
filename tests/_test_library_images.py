import pytest
import library
import hashlib



@pytest.fixture()
def app():
    app = library.create_app()
    salt = app.config["PASSWORD_SALT"]
    admin = {
            "username": "test-admin",
            "password-hash": hashlib.pbkdf2_hmac("sha512", str("test-passwd").encode(), str(salt).encode(), 2 ** 8).hex(),
            "rights": ["server-admin"],
            "blocked": "",
            "waiting": {
                "registration": False,
                "approval": False
                },
            "relationship": {
                "black-list": []
                }
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


def test_image_upload(db, app, client):
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
        assert response.status_code == 200
        assert db.images.find_one({"name": response.json.get("filename")})
        database.images.delete_one({"name": response.json.get("filename")})
    

def test_image_delete(app, db, client, image):
    token = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    response = client.post("/api/image/delete", headers = {"auth-token": token}, json = {"filename": image})
    assert response.status_code == 200
    assert not db.images.find_one({"name": image})


def test_image_download(app, client, image):
    token = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    response = client.post("/api/image/download", headers = {"auth-token": token}, json = {"filename": image})
    assert response.status_code == 200