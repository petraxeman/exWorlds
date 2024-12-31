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



def test_login_success(client, create_user):
    create_user('test-user', 'test-password')

    response = client.post(
        "/api/login", json={"username": "test-user", "password": 'test-password'}
    )
    assert response.status_code == 200
    assert "token" in response.json


def test_login_failure(client, create_user):
    create_user('test-user', 'test-password')
    
    response = client.post(
        "/api/login", json={"username": "wronguser", "password": "wrongpass"}
    )
    
    assert response.status_code == 401


def test_register_allwed_success(client, app, db):
    app.config['REGISTRATION'] = 'allowed'
    
    response = client.post(
        "/api/register", json={"username": "test-user", "password": "test-password"}
    )
    
    assert response.status_code == 200


def test_register_duplicate_user(client, create_user):
    create_user('test-user', 'test-password')
    
    response = client.post(
        "/api/register", json={"username": "test-user", "password": 'test-password'}
    )
    
    assert response.status_code == 401


def test_add_user_to_queue_success(client, create_user):
    _, _, token = create_user('test-admin', 'test-passwd', ['server-admin'])

    response = client.post(
        "/api/account/add-user-to-queue",
        json = {"username": "queueduser"},
        headers = {"auth-token": token},
    )
    assert response.status_code == 200


def test_add_user_to_queue_unauthorized(client, create_user):
    _, _, token = create_user('test-user', 'test-passwd')
    
    response = client.post(
        "/api/account/add-user-to-queue",
        json={"username": "queueduser"},
        headers = {"auth-token": token},
    )
    assert response.status_code == 401