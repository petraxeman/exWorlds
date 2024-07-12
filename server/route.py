from server.app import app, redis_client
from flask import request
import uuid


@app.route("/auth", methods = ["POST"])
def auth() -> str:
    username = request.headers.get('user-login')
    password = request.headers.get('user-password')

    if True:
        pass
    else:
        return {"result": 4}

    token = str(uuid.uuid4())
    redis_client.set(f"user_{username}_auth_token", token, ex = 1800, nx = True)

    token = redis_client.get(f"user_{username}_auth_token").decode()
    return {"result": 1, "token": token}


@app.route("/register", methods = ["POST"])
def register():
    pass