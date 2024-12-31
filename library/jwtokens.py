import datetime
import jwt
from functools import wraps
from flask import request, current_app


def token_required(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        global current_user
        token = request.headers.get("auth-token", None)
        if not token:
            return {"msg": "Valid token is missing"}, 403
        try:
            data = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            expire_date = datetime.datetime.strptime(data["expire_date"], "%d-%m-%Y")

            if expire_date < datetime.datetime.now():
                return {"msg": "Token expired"}, 403

            #postgres = current_app.config["POSTGRES_INST"]
            current_user = current_app.extensions["postgresdb"].get_user_by_username(data["username"])
            if not current_user:
                return {"msg": "Undefined token"}, 403

            request.current_user = current_user
            return fn(*args, **kwargs)
        except Exception as err:
            print(err)
            return {"msg": "Wrong token"}, 403

    return decorator