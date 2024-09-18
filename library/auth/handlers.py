import jwt
import datetime
from typing import Union
from library import utils
from flask import (
    request,
    current_app
)


def process_auth(db, username: str, password: str, password_salt: str) -> Union[dict, int]:
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


def process_registration(db, username: str, password: str, password_salt: str) -> Union[dict, int]:
    if username == None or password == None:
        return {"msg": "Wrong username or password"}, 200
    
    password_hash = utils.get_password_hash(password, password_salt)
    user_document = build_user({"username": username, "password-hash": password_hash})

    if finded_user := db.users.find_one({"username": username, "waiting.registration": True}):
        db.users.update_one(finded_user, {"$set": {"waiting.registration": False}})
        return {"msg": "Registration success"}, 200
    
    match current_app.config.get("REGISTRATION", "forbidden"):
        case "allowed":
            return register_user(db, user_document)
        case "on-request":
            return register_request(db, username, user_document)
        case _:
            return {"msg": "Registration forbidden"}, 401


def register_user(db, user_document: dict) -> Union[dict, int]:
    if db.users.find_one({"username": user_document["username"]}):
        return {"msg": "This login already used."}, 401
    
    db.users.insert_one(user_document)
    return {"msg": "Registration success"}, 200


def register_request(db, username: str, user_document: dict) -> Union[dict, int]:
    if  db.users.find_one({"username": username}):
        return {"msg": "User already exists"}, 401
    user_document["waiting"]["approval"] = True
    user_document["role"] = "user"
    db.users.insert_one(user_document)
    return {"msg": "Registration success"}, 200


def match_rights(required_rights: list, creator_rights: list):
    if {"server-admin", "cant-be-blocked"}.intersection(required_rights):
        if "server-admin" not in creator_rights:
            return False
    if {"add-to-queue", "server-admin"}.intersection(creator_rights):
        return True
    return False


def process_add_user_to_queue(db, required_username: str, required_rights: list, sender_rights: list)  -> Union[dict, int]:
    if not required_username or required_rights == None or required_username == "":
        return {"msg": "Not found expected fields"}, 401

    if db.users.find_one({"username": required_username}):
        return {"msg": "Username already used"}, 401
    
    if not match_rights(required_rights, sender_rights):
        return {"msg": "Unexpected rights"}, 401
    
    user_document = build_user(
        {"username": required_username,
         "password-hash": "",
         "rights": required_rights,
         "waiting": {"registration": True}}
        )
    db.users.insert_one(user_document)
    
    return {"msg": "Registration success"}, 200


def build_user(reference: dict):
    return {
        "username": reference["username"],
        "password-hash": reference.get("password-hash"),
        "rights": reference.get("rights", []),
        "blocked": reference.get("blocked", False),
        "waiting": {
            "registration": reference.get("waiting", {}).get("registration", False),
            "approval": reference.get("waiting", {}).get("approval", False)
            },
        "relationship": {
            "black-list": reference.get("friends", {}).get("black-list", [])
            },
    }