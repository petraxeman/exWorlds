from server.app import app, redis_client, db
from flask import request, send_file, Response
from werkzeug.utils import secure_filename
import uuid, io, jwt, datetime, re
from functools import wraps



# ========================== #
# === ADDITIONAL METHODS === #
# ========================== #

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
            current_user = db.users.find_one({"username": data["username"]}, limit = 1)
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
    username = request.headers.get('User-Login')
    password = request.headers.get('User-Password')

    if db.users.find_one({"username": username, "password": password}) is None:
        return {"msg": "Wrong login or password"}, 401

    expire_data = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    token = jwt.encode({"username": username, "expire_date": expire_data}, key = app.config["JWT_SECRET"], algorithm="HS256")
    return {"token": token}, 200


@app.route("/account/register", methods = ["POST"])
def register():
    username = request.headers.get('User-Login')
    password = request.headers.get('User-Password')
    
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
    username = request.headers.get("Username")

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
@token_required
def get_server_info():
    return {"server_name": app.config["LSERVER_NAME"], "result": 1}



# ==================== #
# === IMAGE ROUTES === #
# ==================== #

# ADD TOKEN AUTHORIZATION AND SYSTEM AUTHOR SUPPORT
@app.route("/images/upload", methods = ["POST"])
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
    return {"name": image_name, "author": current_user["username"]}, 200


# ADD TOKEN AUTHORIZATION
@app.route("/images/info", methods = ["POST"])
@token_required
def image_info():
    image_name = request.headers.get("Image-Name")

    image = db.images.find_one({"image_name": image_name}, limit = 1)
    if image is None:
        return {"msg": "File dont exist"}, 401
    else:
        return {"author": image["author"], "image_name": image["image_name"]}, 200


# ADD TOKEN AUTHORIZATION AND SYSTEM AUTHOR SUPPORT
@app.route("/images/download", methods = ["POST"])
@token_required
def download_image():
    image_name = request.headers.get("Image-Name")

    image = db.images.find_one({"image_name": image_name})
    if image is None:
        return {"result": 18, "message": "File does not exist"}, 401
    return send_file(io.BytesIO(image["image"]), mimetype="image/webp", download_name = "image.webp"), 200


# ====================== #
# === CONTENT ROUTES === #
# ====================== #

@app.route("/structs/create_system", methods = ["POST"])
def create_system():
    data = request.json
    if not db.images.find_one({"name": data["image_name"]}, limit = 1):
        return {"msg": "Image does not exist"}, 401
    if not re.fullmatch("[a-z\-]+", data["codename"]):
        return {"msg": "Wrong codename"}, 401
    if db.structs.find_one({"codename": data["codename"]}):
        return {"msg": "Codename already taken"}
    db.structs.insert_one({"author": current_user["username"], "name": data["name"], "codename": "placeholder", "image": data["image_name"]})
    return {"msg": "System creation success"}, 200