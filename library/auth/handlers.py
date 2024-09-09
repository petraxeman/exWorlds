import jwt
import datetime
from typing import Union
from library import utils
from flask import (
    request,
    current_app
)


def validate_auth(db, username: str, password: str, password_salt: str) -> Union[dict, int]:
    password_hash = utils.get_password_hash(password, password_salt)
    user = db.users.find_one({"username": username, "password-hash": password_hash})

    if user["blocked"] != "":
        if datetime.datetime.strptime(user["blocked"], "%d.%m.%Y") < datetime.now():
            db.users.update_one({"username": username, "password-hash": password}, {"$set": {"blocked": ""}})
        else:
            return {"msg": "You have been blocked", "expire": user["blocked"]}, 200

    if not user:
        return {"msg": "Wrong login or password"}, 401
    
    expire_data = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    token = jwt.encode({"username": username, "expire_date": expire_data}, key = current_app.config["JWT_SECRET"], algorithm="HS256")
    
    return {"token": token}, 200


def validator_add_user_to_queue(db, required_username: str, sender_role: str, required_role: str = "user")  -> bool:
    if required_username != "":
        username = required_username
    else:
        return {"ok": False}
    
    role = "nobody" if required_role == "" else required_role
    
    if sender_role != "admin" and sender_role != "server-admin":
        return {"ok": False}
    
    if db.users.find_one({"username": username}) is not None:
        return {"ok": False}
    
    return {"ok": True, "username": username, "role": role}


def register_user(db, username: str, user_document: dict) -> bool:
    if db.users.find_one({"username": username}):
        return False
    db.users.insert_one(user_document)
    return True


def register_request(db, username: str, user_document: dict) -> bool:
    if  db.users.find_one({"username": username}):
        return False
    user_document["waiting"]["approval"] = True
    user_document["role"] = "user"
    db.users.insert_one(user_document)
    return True


def build_user(reference: dict):
    return {
        "username": reference["username"],
        "password-hash": reference.get("password-hash", ""),
        "role": reference.get("role", "user"),
        "waiting": {
            "registration": reference.get("waiting", {}).get("registration", False),
            "approval": reference.get("waiting", {}).get("approval", False)
            },
        "black-list": reference.get("friends", {}).get("black-list", [])
    }