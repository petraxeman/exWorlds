import datetime
import jwt
from functools import wraps
from flask import (
    request,
    current_app,
    g
)

def token_required(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        global current_user
        token = request.headers.get("auth-token", None)
        if not token:
            return {"msg": "Valid token is missing"}
        try:
            data = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            if datetime.datetime.strptime(data["expire_date"], "%d-%m-%Y") < datetime.datetime.now():
                return {"msg": "Token expired"}, 403
            current_user = current_app.config["MONGODB_INST"].users.find_one({"username": data["username"]})
            if not current_user:
                return {"msg": "Undefined token"}, 403
            request.current_user = current_user
            return fn(*args, **kwargs)
        except Exception as err:
            print(err)
            return {"msg": "Wrong token"}, 403
    return decorator 