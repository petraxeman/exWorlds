from server.app import app, redis_client, db
from flask import request
from werkzeug.utils import secure_filename
import uuid, os, hashlib


    
def user_already_exist(username: str) -> bool:
    result = db.users.find_one({"username": username})
    if result is not None:
        return True
    return False

def get_user(token: str) -> dict:
    return db.users.find_one({"token": token})

def check_token(token: str) -> bool:
    user = db.users.find_one({"token": token})
    if not user:
        return False
    if not redis_client.get(f"user/{user['username']}"):
        return False
    return True

# RETURNS CODES:
# 10 - Wrong login or password
# 11 - Registration Forbidden
# 12 - This login already use
# 13 - Who you are?
# 14 - Wrong token
# 15 - Wrong extension
# 16 - No selected file
# 17 - No file part
# 18 - File dont exist
# ============================================== #
# === USER REGISTRATION AND AUTHENTIFICATION === #
# ============================================== #

@app.route("/umapi/auth", methods = ["POST"])
def auth() -> str:
    username = request.headers.get('user-login')
    password = request.headers.get('user-password')

    if db.users.find_one({"username": username, "password": password}) is None:
        return {"result": 10, "message": "Wrong login or password"}

    token = str(uuid.uuid4())
    redis_client.set(f"user/{username}", token, ex = 1800)
    db.users.update_one({"username": username}, {"$set": {"token": token}}, upsert = True)
    token_ttl = redis_client.ttl(f"user/{username}")
    return {"result": 1, "token": token, "ttl": token_ttl}


@app.route("/umapi/register", methods = ["POST"])
def register():
    username = request.headers.get('user-login')
    password = request.headers.get('user-password')
    
    user_data = {"username": username, "password": password, "await": False}
    if app.config["REGISTRATION"] == "on_request" and (user_obj := db.users.find_one({"username": username})) != None and user_obj["await"] == True:
        db.users.update_one({"username": username}, {"$set": user_data})
    elif app.config["REGISTRATION"] == "allowed":
        if user_already_exist(username):
            return {"result": 12, "message": "This login already use"}
        user_data["role"] = "user"
        db.users.insert_one(user_data)
    else:
        return {"result": 13, "message": "How you are?"}
    
    return {"result": 1}


@app.route("/umapi/register/<login>", methods = ["POST"])
def add_to_register_queue(login: str):
    requesting = get_user(request.headers.get("token"))
    role = request.headers.get("role")

    if requesting["role"] != "admin":
        return {"result": 11, "message": "Registration forbidden"}

    if user_already_exist(login):
        return {"result": 12, "message": "This login already use"}
    
    db.users.insert_one({"username": login, "role": role, "await": True})
    return {"result": 1, "message": f"User <{login}> was created and waiting registration"}


@app.route("/usmapi/token_renew", methods = ["POST"])
def token_renew():
    token = request.headers.get('token')
    user = db.users.find_one({"token": token})
    
    if user is None:
        return {"result": 14, "message": "Wrong token"}
    
    redis_client.set(f"user/{user['username']}", token, ex = 1800)
    ttl = redis_client.ttl(f"user/{user['username']}")
    return {"result": 1, "token": token, "ttl": ttl}


# ===================== #
# === COMMON ROUTES === #
# ===================== #

@app.route("/mapi/get_info", methods = ["POST"])
def get_info():
    return {"server_name": app.config["LSERVER_NAME"], "result": 1}


@app.route("/mapi/upload_image", methods = ["POST"])
def upload_image():
    token = request.headers.get("token")
    if 'file' not in request.files:
        return {"result": 17, "message": "No file part"}
    file = request.files['file']

    if file.filename == '':
        return {"result": 16, "message": "No selected file"}
    
    if file.filename.split(".")[-1] != "png":
        return {"result": 15, "message": "Wrong extension"}
    
    image_hash = hashlib.md5(file.read()).hexdigest()
    image_name = str(uuid.uuid4()) + ".webp"
    db.images.insert_one({"image_hash": image_hash, "image_name": image_name, "image": file.read()})
    return {"result": 1, "message": "Upload Success", "file_name": image_name, "hash": image_hash}


@app.route("/mapi/fetch_image", methods = ["POST"])
def fetch_image():
    token = request.headers.get("token")
    image_hash = request.headers.get("image-hash")
    image_name = request.headers.get("image-name")

    image = db.images.find_one({"image_name": image_name})
    if image is None:
        return {"result": 18, "message": "File dont exist"}
    
    if image_hash != image["image_hash"]:
        return {"result": 19, "message": "Hashes are different"}
    else:
        return {"result": 1, "message": "Hashes are similar"}


@app.route("/mapi/download_image", methods = ["POST"])
def download_image(image_name: str):
    token = request.headers.get("token")
    image_name = request.headers.get("image-name")

    image = db.images.find_one({"image_name": image_name})
    if image is None:
        return {"result": 18, "message": "File dont exist"}
    return {"result": 1, "message": "Operation success", "image": image["image"]}

# ====================== #
# === CONTENT ROUTES === #
# ====================== #

@app.route("/capi/create_schema", methods = ["POST"])
def create_schema():
    return {"result": -1}


@app.route("/capi/create_system", methods = ["POST"])
def create_system():
    if check_token(request.headers.get("token")):
        return {"result": 14}
    
    data = request.data
    print(type(data["image"]))