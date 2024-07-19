from server.app import app, redis_client, db
from flask import request, send_file, Response
from werkzeug.utils import secure_filename
import uuid, os, hashlib, io, jwt
from functools import wraps



def token_required(f):  
    @wraps(f)  
    def decorator(*args, **kwargs):
       token = request.headers.get("Auth-Token", None)
       if not token:  
          return {"msg": "Valid token is missing"}
       try:
          data = jwt.decode(token, app.config["JWT_SECRET"], algorithms=["HS256"])
          if not redis_client.get(f"token/{data['username']}") and not db.users.find_one({"username": data["username"]}):
              raise Exception("Token undefined")
          current_user = db.users.find_one({"username": data["username"]}, limit=1)  
       except Exception as err:
          print(err)
          return {'msg': 'Token is invalid'}
    return decorator 

def user_already_exist(username: str) -> bool:
    result = db.users.find_one({"username": username})
    if result is not None:
        return True
    return False

def get_tuser(token: str) -> bool:
    atoken_user = db.users.find_one({"atoken": token})
    itoken_user = db.users.find_one({"itokens": {"$in": [token]}})
    if not atoken_user and itoken_user:
        return False, "Not Found"
    elif atoken_user and redis_client.get(f"user/{atoken_user['username']}"):
        return True, atoken_user
    elif itoken_user:
        return True, itoken_user
    return False, "Undefined"



# ============================================== #
# === USER REGISTRATION AND AUTHENTIFICATION === #
# ============================================== #

@app.route("/account/auth", methods = ["POST"])
def auth() -> str:
    username = request.headers.get('User-Login')
    password = request.headers.get('User-Password')

    if db.users.find_one({"username": username, "password": password}) is None:
        return {"msg": "Wrong login or password"}, 401

    atoken = str(uuid.uuid4())
    redis_client.set(f"user/{username}", atoken, ex = 1800)
    db.users.update_one({"username": username, "password": password}, {"$set": {"atoken": atoken}}, upsert = True)
    token_ttl = redis_client.ttl(f"user/{username}")
    return {"token": atoken, "ttl": token_ttl}, 200


@app.route("/account/register", methods = ["POST"])
def register():
    username = request.headers.get('User-Login')
    password = request.headers.get('User-Password')
    
    user_object = {"username": username, "password": password, "waiting": False, "role": "user", "itokens": [], "atoken": ""}
    registration_access = app.config["REGISTRATION"]
    if registration_access == "allowed":
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
    else:
        waiting_user = db.users.find_one({"username": username, "waiting": True})
        if waiting_user:
            db.users.update_one({"username": username, "waiting": True}, {"$set": user_object})
            return {"msg": "Registration success"}, 200
        return {"msg": "Registration forbidden"}, 401


@app.route("/account/addUserToQueue", methods = ["POST"])
def add_to_register_queue():
    requester = get_tuser(request.headers.get("Token"))
    username = request.headers.get("Username")
    
    if requester[0] is False:
        return {"msg": "Wrong token"}, 401
    else:
        requester = requester[1]

    if requester and requester["role"] != "admin":
        return {"msg": "Registration forbidden"}; 401

    if db.users.find_one({"username": username}) is not None:
        return {"msg": "This login already use"}, 401
    
    db.users.insert_one({"username": username, "waiting": True})
    return {"msg": f"User <{username}> was created and waiting registration"}, 200


@app.route("/account/extendToken", methods = ["POST"])
def token_extend():
    user = get_tuser(request.headers.get('Token'))
    
    if user[0] is False:
        return {"msg": "Wrong token"}, 401
    else:
        user = user[1]
    
    redis_client.set(f"user/{user['username']}", token, ex = 1800)
    ttl = redis_client.ttl(f"user/{user['username']}")
    return {"result": 1, "token": token, "ttl": ttl}


# ===================== #
# === COMMON ROUTES === #
# ===================== #

@app.route("/server/info", methods = ["POST"])
@token_required
def get_server_info():
    return {"server_name": app.config["LSERVER_NAME"], "result": 1}

@app.route("/debug/test", methods = ["POST"])
@token_required
def get_info():
    print(current_user)
    return {"server_name": app.config["LSERVER_NAME"], "result": 1}

# ==================== #
# === IMAGE ROUTES === #
# ==================== #


# ADD TOKEN AUTHORIZATION AND SYSTEM AUTHOR SUPPORT
@app.route("/images/upload", methods = ["POST"])
@token_required
def upload_image():
    token = request.headers.get("Token")

    if 'image' not in request.files:
        return {"result": 17, "message": "No file part"}
    
    file = request.files['image']
    if file.filename == '':
        return {"result": 16, "message": "No selected file"}
    
    if file.filename.split(".")[-1] != "webp":
        return {"result": 15, "message": "Wrong extension"}

    image_bytes = request.files['image'].read()
    image_hash = hashlib.md5(request.files['image'].read()).hexdigest()
    image_name = str(uuid.uuid4()) + ".webp"
    db.images.insert_one({"image_hash": image_hash, "image_name": image_name, "image": image_bytes})
    return {"result": 1, "message": "Upload Success", "file_name": image_name, "author": "test"}


# ADD TOKEN AUTHORIZATION
@app.route("/images/info", methods = ["POST"])
@token_required
def image_info():
    token = request.headers.get("Token")
    image_name = request.headers.get("Image-Name")

    image = db.images.find_one({"image_name": image_name}, limit = 1)
    if image is None:
        return {"result": 18, "message": "File dont exist"}, 401
    else:
        return {"result": 1, "author": "test", "image_name": image["image_name"]}, 200


# ADD TOKEN AUTHORIZATION AND SYSTEM AUTHOR SUPPORT
@app.route("/images/download", methods = ["POST"])
@token_required
def download_image():
    token = request.headers.get("Token")
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
    token = request.headers.get("Token")
    print(request.json)