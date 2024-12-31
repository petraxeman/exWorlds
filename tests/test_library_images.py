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
    db.execute("DELETE FROM users WHERE username = 'queueduser'")
    db.execute("DELETE FROM images WHERE filename = 'picutre.webp'")


def build_image():
    with open("placeholder.png", "rb") as image:
        body = "\r\n--ImageBoundary\r\n".encode()
        body += "Content-Disposition: form-data; name=\"image\"; filename=\"picture.webp\"\r\n".encode()
        body += "Content-Type: image/webp\r\n\r\n".encode()
        body += image.read()
        body += "\r\n--ImageBoundary--\r\n".encode()
    return body



def test_image_upload(client, create_user):
    _, _, token = create_user('test-user', 'test-passwd')

    body = build_image()
    headers = {"Content-Type": "multipart/form-data; boundary=ImageBoundary", "auth-token": token}
    response = client.post("/api/image/upload", data = body, headers = headers)
    
    assert response.status_code == 200
    

def test_image_by_plain_name_delete(client, create_user):
    _, _, token = create_user('test-user', 'test-passwd')

    body = build_image()
    headers = {"Content-Type": "multipart/form-data; boundary=ImageBoundary", "auth-token": token}
    response = client.post("/api/image/upload", data = body, headers = headers)
    
    response = client.post("/api/image/delete", headers = {"auth-token": token}, json = {"filename": "picture.webp", "path": "/"})

    assert response.status_code == 200


def test_image_by_codename_delete(client, create_user):
    _, _, token = create_user('test-user', 'test-passwd')

    body = build_image()
    headers = {"Content-Type": "multipart/form-data; boundary=ImageBoundary", "auth-token": token}
    response = client.post("/api/image/upload", data = body, headers = headers)
    
    response = client.post("/api/image/delete", headers = {"auth-token": token}, json = {"filename": response.json['filename']})
    
    assert response.status_code == 200


def test_image_download(client, create_user):
    _, _, token = create_user('test-user', 'test-passwd')

    body = build_image()
    headers = {"Content-Type": "multipart/form-data; boundary=ImageBoundary", "auth-token": token}
    response = client.post("/api/image/upload", data = body, headers = headers)
    
    response = client.post("/api/image/download", headers = {"auth-token": token}, json = {"filename": response.json['filename']})

    assert response.status_code == 200