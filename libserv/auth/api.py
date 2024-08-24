import datetime
import jwt
from libserv.jwtokens import token_required
from flask import (
    Blueprint,
    request,
    current_app
    )



bp = Blueprint("api-auth", __name__)

roles = [
    "user", # Can create and delete self created content, or content created in owend systems.
    "admin", # Can create and delete everything.
    "moderator", # In concept. Idea - can delete but can be deleted. Can write reports.
    "server-admin", # Like admin but stronger.
]



@bp.route("/api/login", methods = ["POST"])
@token_required
def login():
    db = current_app.config["MONGODB_INST"]
    
    username = request.json.get('username')
    password = request.json.get('password')

    if db.users.find_one({"username": username, "password": password}) is None:
        return {"msg": "Wrong login or password"}, 401

    expire_data = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    token = jwt.encode({"username": username, "expire_date": expire_data}, key = current_app.config["JWT_SECRET"], algorithm="HS256")
    return {"token": token}, 200


@bp.route("/api/register", methods = ["POST"])
def register():
    db = current_app.config["MONGODB_INST"]

    username = request.json.get('username')
    password = request.json.get('password')
    
    user_object = {"username": username, "password": password, "waiting-registration": False}
    registration_access = current_app.config["REGISTRATION"]
    
    if db.users.find_one({"username": username, "waiting-registration": True}):
        db.users.update_one({"username": username, "waiting-registration": True}, {"$set": user_object})
        return {"msg": "Registration success"}, 200
    
    if registration_access == "allowed":
        finded_user = db.users.find_one({"username": username})
        if finded_user:
            return {"msg": "Login already use"}, 401
        db.users.insert_one(user_object)
        return {"msg": "Registration success"}, 200
    
    elif registration_access == "on_request":
        finded_user = db.users.find_one({"username": username})
        if finded_user:
            return {"msg": "Login already use"}, 401
        user_object["awaiting-approval"] = True
        user_object["role"] = "user"
        db.users.insert_one(user_object)
        return {"msg": "Request created"}, 200
    
    return {"msg": "Registration forbidden"}, 401


@bp.route("/api/account/add-user-to-reg-queue", methods = ["POST"])
@token_required
def add_user_to_register_queue():
    db = current_app.config["MONGODB_INST"]

    username = request.json.get("username", "")
    role = request.json.get("role", "nobody")
    if role == "":
        role = "nobody"

    if username == "":
        return {"msg": "Username does not exists."}
    
    if "admin" != request.current_user["role"] and "server-admin" != request.current_user["role"]:
        return {"msg": "Registration forbidden"}; 401

    if db.users.find_one({"username": username}) is not None:
        return {"msg": "This login already use"}, 401
    
    db.users.insert_one({"username": username, "waiting-registration": True, "role": role})
    return {"msg": f"User <{username}> was created and waiting registration"}, 200