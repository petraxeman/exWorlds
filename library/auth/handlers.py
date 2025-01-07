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
    user = db.fetchone("SELECT * FROM users WHERE username=%s AND password_hash=%s", (username, password_hash))
    
    if not user:
        return {"msg": "Wrong login or password"}, 401
    
    user = user._asdict()
    
    if user["banned"]:
        if datetime.datetime.strptime(user["blocked"], "%d.%m.%Y") < datetime.now():
            db.execute("UPDATE users SET banned = NULL WHERE uid = %s", (user["uid"],))
        else:
            return {"msg": "You have been banned"}, 200
    
    expire_data = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    token = jwt.encode({"username": username, "expire_date": expire_data}, key = current_app.config["JWT_SECRET"], algorithm="HS256")
    
    return {"token": token}, 200


def process_registration(db, username: str, password: str, password_salt: str) -> Union[dict, int]:
    if username == None or password == None:
        return {"msg": "Wrong username or password"}, 200
    
    password_hash = utils.get_password_hash(password, password_salt)
    finded_user = db.fetchone('SELECT * FROM users WHERE username = %s', (username,))
    
    if finded_user:
        finded_user = finded_user._asdict()
        if finded_user["waiting"]["registration"] == True:
            db.execute("""UPDATE users SET waiting = waiting || '{"registration": false}', password_hash = %s WHERE username = %s""", (password_hash, username,))
            return {"msg": "Registration success"}, 200
        else:
            return {"msg": "This login already in use."}, 401
    
    match current_app.config.get("REGISTRATION", "forbidden"):
        case "allowed":
            return register_user(db, username, password_hash)
        case "on-request":
            return register_request(db, username, password_hash)
        case _:
            return {"msg": "Registration forbidden"}, 401


def register_user(db, username: str, password_hash: str) -> Union[dict, int]:
    try:
        db.execute("SELECT add_user(%s, %s)", (username, password_hash,))
        return {"msg": "Registration success"}, 200
    except:
        return {"msg": "Somthing went wrong. Try again later"}, 500


def register_request(db, username: str, password_hash: str) -> Union[dict, int]:
    try:
        db.execute("SELECT add_user(%s, %s, aproval=>true)", username, password_hash)
        return {"msg": "Registration success. Wait when your account be aproved"}, 200
    except:
        return {"msg": "Somthing went wrong. Try again later"}, 500


def process_add_user_to_queue(db, required_username: str, sender_rights: list)  -> Union[dict, int]:
    if not required_username or required_username == "":
        return {"msg": "Not found expected fields"}, 401
    
    if not {'server-admin', 'add-to-queue', 'any-account'}.intersection(sender_rights):
        return {"msg": "You can't do that."}, 401
    
    if db.fetchone('SELECT * FROM users WHERE username = %s', (required_username,)):
        return {"msg": "Username already used"}, 401
    
    try:
        db.execute("SELECT add_user(%s, '', registration=>true)", (required_username,))
        return {"msg": "Registration success"}, 200
    except:
        return {"msg": "Somthing went wrong. Try again later"}, 500