import datetime
import jwt
import hashlib
from libserv.jwtokens import token_required
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
    password_hash = get_hash(request.json.get('password'))

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
    password_hash = get_hash(request.json.get('password'))
    user_document = build_user({"username": username, "password-hash": password_hash})
    
    if finded_user := db.users.find_one({"username": username, "waiting.registration": True}):
        print("Register here")
        user_document["role"] = finded_user["role"]
        db.users.update_one(finded_user, {"$set": user_document})
        return {"msg": "Registration success"}, 200
    
    match current_app.config.get("REGISTRATION", "forbidden"):
        case "allowed":
            result = register_user(db, request.json, user_document)
        case "on-request":
            result = register_request(db, request.json, user_document)
        case _:
            result = False
        
    if not result:
        return {"msg": "Somthing went wrong. Try again later."}, 401
    
    return {"msg": "Registration success"}, 200

def register_user(db, rjson: dict, user_document: dict) -> bool:
    if db.users.find_one({"username": rjson.get("username")}):
        return False
    db.users.insert_one(user_document)
    return True

def register_request(db, rjson: dict, user_document: dict) -> bool:
    if  db.users.find_one({"username": rjson.get("username")}):
        return False
    user_document["waiting"]["approval"] = True
    user_document["role"] = "user"
    db.users.insert_one(user_document)
    return True


# ADD USER TO QUEUE
@bp.route("/api/account/add-user-to-queue", methods = ["POST"])
@token_required
def add_user_to_register_queue():
    db = current_app.config["MONGODB_INST"]
    
    result: bool = validate_add_user_to_queue(db, request.json, request.current_user)
    if not result["ok"]:
        return {"msg": "Somthing went wrong. Try again later."}
    
    user_document = build_user({
        "username": result["username"],
        "role": result["role"],
        "waiting": {"registration": True}
        })
    db.users.insert_one(user_document)
    return {"msg": f"User <{result['username']}> was created and waiting registration"}, 200

def validate_add_user_to_queue(db, rjson: dict, current_user: dict) -> bool:
    sender_role = current_user["role"]
    
    username = "undefined"
    if (rusername := rjson.get("username", "")) != "":
        username = rusername
    else:
        return {"ok": False}
    
    role = "nobody"
    if (rrole := request.json.get("role", "")) != "":
        role = rrole
    
    if sender_role != "admin" and sender_role != "server-admin":
        return {"ok": False}
    
    if db.users.find_one({"username": username}) is not None:
        return {"ok": False}
    return {"ok": True, "username": username, "role": role}



def build_user(reference: dict):
    return {
        "username": reference["username"],
        "password-hash": reference.get("password-hash", ""),
        "role": reference.get("role", "user"),
        "waiting": {
            "registration": reference.get("waiting", {}).get("registration", False),
            "approval": reference.get("waiting", {}).get("approval", False)
            },
        "friends": {
            "list": reference.get("friends", {}).get("list", []),
            "sended": reference.get("friends", {}).get("sended", []),
            "recieved": reference.get("friends", {}).get("recieved", [])
            },
    }


def get_hash(password: str) -> str:
    return hashlib.md5(str(password).encode()).hexdigest()