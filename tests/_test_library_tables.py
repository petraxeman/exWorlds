import pytest
import library
import hashlib



@pytest.fixture()
def app():
    app = library.create_app()
    yield app


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
def image(app, client, admin):
    database = app.config["MONGODB_INST"]
    with open("placeholder.png", "rb") as image:
        body = "\r\n--ImageBoundary\r\n".encode()
        body += "Content-Disposition: form-data; name=\"image\"; filename=\"picture.webp\"\r\n".encode()
        body += "Content-Type: image/webp\r\n\r\n".encode()
        body += image.read()
        body += "\r\n--ImageBoundary--\r\n".encode()
        headers = {"Content-Type": "multipart/form-data; boundary=ImageBoundary", "auth-token": admin}
        response = client.post("/api/image/upload", data = body, headers = headers)
        filename = response.json.get("filename")
        yield filename
        database.images.delete_one({"name": filename})


@pytest.fixture()
def user(app, client):
    salt = app.config["PASSWORD_SALT"]
    test_user = {
            "username": "test-user",
            "password-hash": hashlib.pbkdf2_hmac("sha512", "test-passwd".encode(), str(salt).encode(), 2 ** 8).hex(),
            "rights": [],
            "blocked": "",
            "waiting": {
                "registration": False,
                "approval": False
                },
            "relationship": {
                "black-list": [],
                }
        }
    app.config["MONGODB_INST"].users.insert_one(test_user)
    token = auth(client, "test-user", "test-passwd")
    yield token


@pytest.fixture()
def admin(app, client):
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
    token = auth(client, "test-admin", "test-passwd")
    yield token


@pytest.fixture(autouse=True)
def run_after(db):
    db.users.delete_one({"username": "test-user"})
    db.users.delete_one({"username": "test-admin"})
    db.packs.delete_many({"type": "game-system", "codename": "game-system"})
    db.tables.delete_one({"codename": "test-table"})
    yield
    db.users.delete_one({"username": "test-user"})
    db.users.delete_one({"username": "test-admin"})
    db.packs.delete_many({"type": "game-system", "codename": "game-system"})
    db.tables.delete_one({"codename": "test-table"})



def build_test_game_system(image_name, name: str = "Game system"):
    return {
        "name": name,
        "codename": "game-system",
        "image-name": image_name,
        "type": "game-system",
        }


def build_test_table(username: str):
    return {
        "name": "Table",
        "codename": "test-table",
        "owner": username,
        "reference": {"points": ["game-system"], "exp": "pack"},
        "common": {
            "search-fields": [],
            "short-view": {},
            "table-icon": "",
            "display": "list"
        },
        "params": {
            "properties": {},
            "macros": {},
            "schema": {},
            "table-fields": {}
        }
    }


def elevate_rights(db, username: str, rights_to_add: list):
    user = db.users.find_one({"username": username})
    rights = user.get("rights", [])
    rights.extend(rights_to_add)
    db.users.update_one({"username": username}, {"$set": {"rights": rights}})


def create_gs(client, image, token):
    gs = build_test_game_system(image)
    response = client.post("/pack/upload", headers = {"auth-token": token}, json = gs)
    assert response.status_code == 200
    return gs


def auth(client, login: str, passwd: str):
    return client.post("/api/login", json = {"username": login, "password": passwd}).json.get("token")



def test_table_create_by_user_with_rights(db, client, user, image):
    elevate_rights(db, "test-user", ["create-table", "create-pack"])
    assert create_gs(client, image, user)
    table = build_test_table("test-user")
    response = client.post("/table/upload", headers = {"auth-token": user}, json = table)
    assert response.status_code == 200
    assert db.tables.find_one({"codename": "test-table"})


def test_table_update_by_creator(db, client, user, image):
    elevate_rights(db, "test-user", ["create-table", "create-pack"])
    assert create_gs(client, image, user)
    table = build_test_table("test-user")
    response = client.post("/table/upload", headers = {"auth-token": user}, json = table)
    assert response.status_code == 200
    assert db.tables.find_one({"codename": "test-table"})
    table["name"] = "Table changed"
    response = client.post("/table/upload", headers = {"auth-token": user}, json = table)
    assert response.status_code == 200
    assert db.tables.find_one({"codename": "test-table"}).get("name") == "Table changed"


def test_table_update_by_admin(db, client, user, admin, image):
    elevate_rights(db, "test-user", ["create-table", "create-pack"])
    assert create_gs(client, image, user)
    table = build_test_table("test-user")
    response = client.post("/table/upload", headers = {"auth-token": user}, json = table)
    assert response.status_code == 200
    assert db.tables.find_one({"codename": "test-table"})
    table["name"] = "Table changed"
    response = client.post("/table/upload", headers = {"auth-token": admin}, json = table)
    assert response.status_code == 200
    assert db.tables.find_one({"codename": "test-table"}).get("name") == "Table changed"


def test_table_create_by_user_without_rights(db, client, image, user):
    elevate_rights(db, "test-user", ["create-pack"])
    assert create_gs(client, image, user)
    table = build_test_table("test-user")
    response = client.post("/table/upload", headers = {"auth-token": user}, json = table)
    assert response.status_code != 200
    assert not db.tables.find_one({"codename": "test-table"})


def test_table_get(db, client, image, user):
    elevate_rights(db, "test-user", ["create-table", "create-pack"])
    assert create_gs(client, image, user)
    table = build_test_table("test-user")
    client.post("/table/upload", headers = {"auth-token": user}, json = table)
    query = {"path-list": [{"points": ["game-system"], "exp": "pack"}]}
    response = client.post("/table/get", headers = {"auth-token": user}, json = query)
    assert response.status_code == 200


def test_table_get_hash(db, client, image, user):
    elevate_rights(db, "test-user", ["create-table", "create-pack"])
    assert create_gs(client, image, user)
    table = build_test_table("test-user")
    client.post("/table/upload", headers = {"auth-token": user}, json = table)
    path = {"points": ["game-system"], "exp": "pack"}
    query = {"tables": [{"codename": "test-table", "reference": path}]}
    response = client.post("/table/get-hash", headers = {"auth-token": user}, json = query)
    assert response.status_code == 200


def test_table_delete(db, client, image, user):
    elevate_rights(db, "test-user", ["create-table", "create-pack"])
    assert create_gs(client, image, user)
    table = build_test_table("test-user")
    client.post("/table/upload", headers = {"auth-token": user}, json = table)
    query = {"points": ["game-system", "test-table"], "exp": "table"}
    response = client.post("/table/delete", headers = {"auth-token": user}, json = query)
    assert response.status_code == 200
    assert not db.tables.find_one({"codename": "test-table"})