from server.app import app, redis_client, db
from flask import request
import uuid


    
def user_already_exist(username: str) -> bool:
    result = db.users.find_one({"username": username})
    if result is not None:
        return True
    return False

def get_user(token: str) -> dict:
    return db.users.find_one({"token": token})


# ====================================== $
# USER REGISTRATION AND AUTHENTIFICATION #
# ====================================== $

@app.route("/auth", methods = ["POST"])
def auth() -> str:
    username = request.headers.get('user-login')
    password = request.headers.get('user-password')

    if db.users.find_one({"username": username, "password": password}) is None:
        return {"result": 10, "message": "Wrong login or password"}

    token = str(uuid.uuid4()); redis_key = f"user/{username}"
    redis_client.set(redis_key, token, ex = 1800, nx = True)
    token = redis_client.get(redis_key).decode()
    db.users.update_one({"username": username}, {"$set": {"token": token}}, upsert = True)
    token_ttl = redis_client.ttl(redis_key)
    return {"result": 1, "token": token, "ttl": token_ttl}


@app.route("/register", methods = ["POST"])
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


@app.route("/register/<login>", methods = ["POST"])
def add_to_register_queue(login: str):
    requesting = get_user(request.headers.get("token"))
    role = request.headers.get("role")

    if requesting["role"] != "admin":
        return {"result": 11, "message": "Registration forbidden"}

    if user_already_exist(login):
        return {"result": 12, "message": "This login already use"}
    
    db.users.insert_one({"username": login, "role": role, "await": True})
    return {"result": 1, "message": f"User <{login}> was created and waiting registration"}


@app.route("/create_schema", methods = ["POST"])
def create_schema():
    pass



# ============= #
# COMMON ROUTES #
# ============= #

@app.route("/rlapi/get_info", methods = ["POST"])
def get_info():
    return {"server_name": app.config["LSERVER_NAME"], "result": 1}