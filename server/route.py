from server import app, db
from flask import request, send_file, Response
from werkzeug.utils import secure_filename
import uuid, io, jwt, datetime, re, json, hashlib
from functools import wraps



def token_required(fn):  
    @wraps(fn)  
    def decorator(*args, **kwargs):
        global current_user
        token = request.headers.get("Auth-Token", None)
        if not token:  
            return {"msg": "Valid token is missing"}
        try:
            data = jwt.decode(token, app.config["JWT_SECRET"], algorithms=["HS256"])
            if datetime.datetime.strptime(data["expire_date"], "%d-%m-%Y") < datetime.datetime.utcnow():
                return {"msg": "Token expired"}, 401
            current_user = db.users.find_one({"username": data["username"]})
            if not current_user:
                return {"msg": "Undefined token"}, 401
            return fn(*args, **kwargs)
        except Exception as err:
            print(err)
            return {"msg": "Wrong token"}, 401
    return decorator 



# ============================================== #
# === USER REGISTRATION AND AUTHENTIFICATION === #
# ============================================== #

@app.route("/account/auth", methods = ["POST"])
def auth() -> str:
    username = request.json.get('username')
    password = request.json.get('password')

    if db.users.find_one({"username": username, "password": password}) is None:
        return {"msg": "Wrong login or password"}, 401

    expire_data = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    token = jwt.encode({"username": username, "expire_date": expire_data}, key = app.config["JWT_SECRET"], algorithm="HS256")
    return {"token": token}, 200


@app.route("/account/registration", methods = ["POST"])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    
    user_object = {"username": username, "password": password, "waiting": False, "role": "user"}
    registration_access = app.config["REGISTRATION"]
    if db.users.find_one({"username": username, "waiting": True}):
        db.users.update_one({"username": username, "waiting": True}, {"$set": user_object})
        return {"msg": "Registration success"}, 200
    elif registration_access == "allowed":
        finded_user = db.users.find_one({"username": username})
        if finded_user:
            return {"msg": "Login already use"}, 401
        db.users.insert_one(user_object)
        return {"msg": "Registration success"}, 200
    elif registration_access == "on_request":
        # AND SOME CODE HERE ....
        # HERE NEED TO CREATE METHOD OR WRITE CODE 
        # WHO CREATE REQUEST FOR ADMIN AND MODERATORS
        pass
    return {"msg": "Registration forbidden"}, 401


@app.route("/account/addUserToQueue", methods = ["POST"])
@token_required
def add_to_register_queue():
    username = request.data.get("username")

    if current_user["role"] != "admin":
        return {"msg": "Registration forbidden"}; 401

    if db.users.find_one({"username": username}) is not None:
        return {"msg": "This login already use"}, 401
    
    db.users.insert_one({"username": username, "waiting": True})
    return {"msg": f"User <{username}> was created and waiting registration"}, 200



# ===================== #
# === COMMON ROUTES === #
# ===================== #

@app.route("/server/info", methods = ["POST"])
def get_server_info():
    return {"server_name": app.config["LSERVER_NAME"]}, 200



# ==================== #
# === IMAGE ROUTES === #
# ==================== #

# ADD TOKEN AUTHORIZATION AND SYSTEM AUTHOR SUPPORT
@app.route("/image/upload", methods = ["POST"])
@token_required
def upload_image():
    if 'image' not in request.files:
        return {"msg": "No file part"}, 401
    
    file = request.files['image']
    if file.filename == '':
        return {"msg": "No selected file"}, 401
    
    if file.filename.split(".")[-1] != "webp":
        return {"msg": "Wrong extension"}, 401

    image_bytes = request.files['image'].read()
    image_name = str(uuid.uuid4()) + ".webp"
    db.images.insert_one({"author": current_user["username"], "name": image_name, "image": image_bytes})
    return {"filename": image_name, "author": current_user["username"]}, 200


# ADD TOKEN AUTHORIZATION
@app.route("/image/info", methods = ["POST"])
@token_required
def image_info():
    filename = request.json.get("filename")
    image = db.images.find_one({"name": filename})
    if not image:
        return {"msg": "File dont exist"}, 401
    return {"author": image["author"], "image_name": image["name"]}, 200


# ADD TOKEN AUTHORIZATION AND SYSTEM AUTHOR SUPPORT
@app.route("/image/download", methods = ["POST"])
@token_required
def download_image():
    filename = request.json.get("filename")
    image = db.images.find_one({"name": filename})
    if image is None:
        return {"msg": "File does not exist"}, 401
    return send_file(io.BytesIO(image["image"]), mimetype="image/webp", download_name = "image.webp"), 200



# ===================== #
# === MACROS ROUTES === #
# ===================== #

@app.route("/macro/upload", methods = ["POST"])
@token_required
def upload_macros():
    return {}, 200


@app.route("/macro/get", methods = ["POST"])
@token_required
def get_macros():
    pass



# ===================== #
# === SYSTEM ROUTES === #
# ===================== #

@app.route("/gameSystem/create", methods = ["POST"])
@token_required
def create_system():
    data = request.json
    if not db.images.find_one({"name": data["image_name"]}):
        return {"msg": "Image does not exist"}, 401
    if not re.fullmatch("[0-9a-z\-_]+", data["codename"]):
        print(data["codename"])
        return {"msg": "Wrong codename"}, 401
    if db.structs.find_one({"author": current_user["username"], "codename": data["codename"], "type": "game_system"}):
        return {"msg": "Codename already taken"}
    new_system = {
        "name": data["name"],
        "codename": data["codename"],
        "image_name": data["image_name"]
        }
    hash = hashlib.md5(str(new_system).encode()).hexdigest()
    new_system["type"] = "game_system"
    new_system["author"] = current_user["username"]
    new_system["hash"] = hash
    db.structs.insert_one(new_system)
    return {"hash": hash}, 200


@app.route("/gameSystem/get", methods = ["POST"])
@token_required
def get_system():
    codename = request.json.get("codename")
    if not codename:
        return {"msg": "Undefined system"}, 401
    system = db.structs.find_one({"type": "game_system", "codename": codename})
    if not system:
        return {"msg": "Undefined system"}, 401
    del system["type"]
    del system["_id"]
    system["can_change"] = True if current_user["username"] == system["author"] else False
    return system, 200


@app.route("/gameSystem/getHash", methods = ["POST"])
@token_required
def get_system_hash():
    codename = request.json.get("codename")
    if not codename:
        return {"msg": "Undefined system"}, 401
    system = db.structs.find_one({"type": "game_system", "codename": codename})
    if not system:
        return {"msg": "Undefined system"}, 401
    return {"hash": system["hash"]}, 200


@app.route("/gameSystems/get", methods = ["POST"])
@token_required
def get_systems():
    data = request.json
    page = data.get("page", 0)
    systems = db.structs.find({"type": "game_system"}).skip(10 * page).limit(10)
    codenames = [el["codename"] for el in systems]
    return {"systems": codenames}, 200


@app.route("/gameSystems/getCount", methods = ["POST"])
@token_required
def get_systems_count():
    count = db.structs.count_documents({"type": "game_system"})
    return {"count": count}



# ==================== #
# === TABLE ROUTES === #
# ==================== #


@app.route("/gameSystem/getTable", methods = ["POST"])
@token_required
def get_table():
    pass


@app.route("/gameSystem/getTables", methods = ["POST"])
@token_required
def get_tables():
    system_codename = request.json.get("system_codename")
    schemas = db.structs.find({"type": "schema", "game_system": system_codename})
    schemas = [{"codename": schema["codename"], "icon": schema["icon"], "name": schema["name"], } for schema in schemas]
    return {"schemas": schemas}, 200



def parse_table(table: list):
    return {} # Должен вернуть список полей и результат проверки

def parse_row(row: list):
    pass

@app.route("/gameSystem/createTable", methods = ["POST"])
@token_required
def create_table():
    parse_table(request.json.get("table", []))
    return {}, 200
