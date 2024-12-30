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



def test_auth(app, client):
    response = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"})
    assert response.status_code == 200


def test_wrong_auth1(client):
    response = client.post("/api/login", json = {"username": "test-wrong-user", "password": "test-passwd"})
    assert response.status_code != 200


def test_register_allowed(app, db, client):
    app.config["REGISTRATION"] = "allowed"
    response = client.post("/api/register", json = {"username": "test-user", "password": "test-passwd"})
    assert db.users.find_one({"username": "test-user"})
    db.users.delete_one({"username": "test-user"})
    assert response.status_code == 200


def test_register_forbidden(app, db, client):
    app.config["REGISTRATION"] = "forbidden"
    response = client.post("/api/register", json = {"username": "test-user", "password": "test-passwd"})
    db.users.delete_one({"username": "test-user"})
    assert response.status_code != 200


def test_register_on_request(app, db, client):
    app.config["REGISTRATION"] = "on-request"
    response = client.post("/api/register", json = {"username": "test-user", "password": "test-passwd"})
    assert db.users.find_one({"username": "test-user"})
    db.users.delete_one({"username": "test-user"})
    assert response.status_code == 200


def test_add_user_to_queue(app, db, client):
    app.config["REGISTRATION"] = "forbidden"
    token = client.post("/api/login", json = {"username": "test-admin", "password": "test-passwd"}).json.get("token")
    response = client.post("/api/account/add-user-to-queue", json = {"username": "test-user", "rights": []}, headers = {"auth-token": token})
    assert db.users.find_one({"username": "test-user"})
    db.users.delete_one({"username": "test-user"})
    assert response.status_code == 200



