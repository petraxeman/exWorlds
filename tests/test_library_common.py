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



def test_server_inf0(app, db, client):
    response = client.post("/api/server/info")
    assert response.status_code == 200