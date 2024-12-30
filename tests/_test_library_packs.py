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
            "lists": {
                "favorites": [],
                "likes": []
            },
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
            "lists": {
                "favorites": [],
                "likes": []
            },
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
    yield
    db.packs.delete_many({"type": "game-system", "codename": "game-system"})
    db.users.delete_one({"username": "test-user"})
    db.users.delete_one({"username": "test-admin"})


def build_test_gs(image_name, owner: str = "test-admin", name: str = "Game system", codename: str = "game-system"):
    return {
        "name": name,
        "codename": codename,
        "image-name": image_name,
        "type": "game-system",
        "reference": "",
        "path": "pack://" + codename,
        "hidden": False,
        "freezed": False,
        "likes": 0,
        "last-update": 0,
        "owner": owner,
        "readctors": [],
    }


def auth(client, login: str, passwd: str):
    return client.post("/api/login", json = {"username": login, "password": passwd}).json.get("token")


def test_create_by_admin(db, client, image, admin):
    pack = build_test_gs(image)
    response = client.post("/pack/upload", headers = {"auth-token": admin}, json = pack)
    assert response.status_code == 200
    assert response.json["hash"]
    assert db.packs.find_one({"type": "game-system", "codename": "game-system"})


def test_create_by_user_with_rights(db, client, image, user):
    db.users.update_one({"username": "test-user"}, {"$set": {"rights": ["create-pack"]}})
    pack = build_test_gs(image)
    response = client.post("/pack/upload", headers = {"auth-token": user}, json = pack)
    assert response.status_code == 200
    assert response.json["hash"]
    assert db.packs.find_one({"type": "game-system", "codename": "game-system"})


def test_create_by_user_without_rights(client, image, user):
    pack = build_test_gs(image)
    response = client.post("/pack/upload", headers = {"auth-token": user}, json = pack)
    assert response.status_code != 200
    assert response.json.get("msg") == "You can't do that."


def test_changing(db, client, image, admin):
    # Creating game system
    body = build_test_gs(image, name = "Game system 1")
    response = client.post("/pack/upload", headers = {"auth-token": admin}, json = body)
    assert response.status_code == 200
    assert db.packs.find_one({"name": "Game system 1", "path": "pack://game-system"})
    # Changing game system name
    body["name"] = "Game system 2"
    response = client.post("/pack/upload", headers = {"auth-token": admin}, json = body)
    assert response.status_code == 200
    assert db.packs.find_one({"name": "Game system 2", "path": "pack://game-system"})


def test_changing_user_pack_by_admin(db, client, image, admin, user):
    db.users.update_one({"username": "test-user"}, {"$set": {"rights": ["create-pack"]}})
    # User create a system 
    body = build_test_gs(image, name = "Game system 1")
    response = client.post("/pack/upload", headers = {"auth-token": user}, json = body)
    assert response.status_code == 200
    assert db.packs.find_one({"name": "Game system 1", "codename": "game-system", "type": "game-system"})
    # Admin change them
    body["name"] = "Game system 2"
    response = client.post("/pack/upload", headers = {"auth-token": admin}, json = body)
    assert response.status_code == 200
    assert db.packs.find_one({"name": "Game system 2", "codename": "game-system", "type": "game-system"})


def test_get(client, image):
    admin = auth(client, "test-admin", "test-passwd")
    body = build_test_gs(image)
    client.post("/pack/upload", headers = {"auth-token": admin}, json = body)
    path1 = "pack://game-system"
    path2 = "pack://not-exists"
    response = client.post("/pack/get", headers = {"auth-token": admin}, json = {"path-list": [path1, path2]})
    assert response.status_code == 200


def test_get_wrong(client, image, admin):
    body = build_test_gs(image)
    client.post("/pack/upload", headers = {"auth-token": admin}, json = body)
    path = {"points": ["not-exists"], "exp": "pack"}
    response = client.post("/pack/get", headers = {"auth-token": admin}, json = {"path-list": [path]})
    assert response.status_code != 200
    assert response.json.get("msg", "") == "Undefined packs"


def test_get_hash(client, image, admin):
    body = build_test_gs(image)
    client.post("/pack/upload", headers = {"auth-token": admin}, json = body)
    path = "pack://game-system"
    response = client.post("/pack/get-hash", headers = {"auth-token": admin}, json = {"path-list": [path]})
    assert response.status_code == 200
    assert response.json["hashes"]


def test_get_by_pages(client, image, admin):
    body = build_test_gs(image)
    client.post("/pack/upload", headers = {"auth-token": admin}, json = body)
    response = client.post("/pack/get-by-page", headers = {"auth-token": admin}, json = {"type": "game-system", "page": "1"})
    assert response.status_code == 200
    assert response.json["codenames"]


def test_get_count(client, image, admin):
    body = build_test_gs(image)
    client.post("/pack/upload", headers = {"auth-token": admin}, json = body)
    response = client.post("/pack/get-count", headers = {"auth-token": admin}, json = {"type": "game-system"})
    assert response.status_code == 200
    assert response.json["count"]


def test_delete(client, image, admin):
    body = build_test_gs(image)
    client.post("/pack/upload", headers = {"auth-token": admin}, json = body)
    client.post("/pack/toggle/like", headers = {"auth-token": admin}, json = {"path": "pack://game-system"})
    client.post("/pack/toggle/favorite", headers = {"auth-token": admin}, json = {"path": "pack://game-system"})
    response = client.post("/pack/delete", headers = {"auth-token": admin}, json = {"path": "pack://game-system"})
    print(response.json)
    assert response.status_code == 200


# TODO: Write here tests for
#   - Favorite
#   - Likes
#   - Hide
#   - Freeze

def test_favorite(client):
    pass


def ffc(image, n, cn, h = False, l = 0, r = []):
    return {
        "name": n,
        "codename": cn,
        "image-name": image,
        "type": "game-system",
        "reference": "",
        "path": "pack://" + cn,
        "hidden": h,
        "freezed": False,
        "likes": l,
        "last-update": 0,
        "owner": "test-admin",
        "redactors": r}


def _test_additional_actions(db, client, image, admin, user):
    import time

    print()
    
    ft = time.time()
    for i in range(10000):
        gs = ffc(image, f"Cool system {i}", f"sys-{i}")
        client.post("/pack/upload", headers = {"auth-token": admin}, json = gs)
    print("Time add:", time.time() - ft)
    
    
    for i in [1, 100, 1000]:
        ft = time.time()
        r = client.post("/pack/get-by-page", headers = {"auth-token": admin}, json = {"page": 1, "type": "game-system", "search": f"Cool system {i}"})
        print(f"Get by {i}:", time.time() - ft)
        
    ft = time.time()
    for i in range(10000):
        db.packs.delete_one({"codename": f"sys-{i}"})
    print("Time del:", time.time() - ft)