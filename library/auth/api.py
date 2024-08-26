import datetime
import jwt
import hashlib
from library.jwtokens import token_required
from library.auth import handlers
from library import utils
from flask import (
    Blueprint,
    request,
    current_app
    )

bp = Blueprint("api-auth", __name__)



@bp.route("/api/login", methods = ["POST"])
def login():
    db = current_app.config["MONGODB_INST"]
    
    username = request.json.get('username')
    password_hash = utils.get_password_hash(request.json.get('password'), current_app.config["PASSWORD_SALT"])

    if db.users.find_one({"username": username, "password-hash": password_hash}) is None:
        return {"msg": "Wrong login or password"}, 401

    expire_data = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    token = jwt.encode({"username": username, "expire_date": expire_data}, key = current_app.config["JWT_SECRET"], algorithm="HS256")
    return {"token": token}, 200


# USER REGISTRATION
@bp.route("/api/register", methods = ["POST"])
def register():
    if not request.json.get("username", False) or not request.json.get("password", False):
        return {"msg": "No username or password"}, 401
    
    db = current_app.config["MONGODB_INST"]

    username = request.json.get('username')
    password_hash = utils.get_password_hash(request.json.get('password'), current_app.config["PASSWORD_SALT"])
    user_document = handlers.build_user({"username": username, "password-hash": password_hash})
    
    if finded_user := db.users.find_one({"username": username, "waiting.registration": True}):
        user_document["role"] = finded_user["role"]
        db.users.update_one(finded_user, {"$set": user_document})
        return {"msg": "Registration success"}, 200
    
    match current_app.config.get("REGISTRATION", "forbidden"):
        case "allowed":
            result = handlers.register_user(db, request.json.get("username", ""), user_document)
        case "on-request":
            result = handlers.register_request(db, request.json.get("username", ""), user_document)
        case _:
            result = False
        
    if not result:
        return {"msg": "Somthing went wrong. Try again later."}, 401
    
    return {"msg": "Registration success"}, 200




# ADD USER TO QUEUE
@bp.route("/api/account/add-user-to-queue", methods = ["POST"])
@token_required
def add_user_to_register_queue():
    db = current_app.config["MONGODB_INST"]
    
    result: bool = handlers.validator_add_user_to_queue(
        db,
        request.json.get("username", ""),
        request.current_user.get("role", ""),
        request.json.get("role", "")
        )
    
    if not result["ok"]:
        return {"msg": "Somthing went wrong. Try again later."}
    
    user_document = handlers.build_user({
        "username": result["username"],
        "role": result["role"],
        "waiting": {"registration": True}
        })
    
    db.users.insert_one(user_document)
    return {"msg": f"User <{result['username']}> was created and waiting registration"}, 200