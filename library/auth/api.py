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
    password_salt = current_app.config["PASSWORD_SALT"]
    username = request.json.get('username')
    password = request.json.get('password')
    result = handlers.process_auth(db, username, password, password_salt)
    return result


@bp.route("/api/register", methods = ["POST"])
def register():
    if not request.json.get("username", False) or not request.json.get("password", False):
        return {"msg": "No username or password"}, 401
    db = current_app.config["MONGODB_INST"]
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    return handlers.process_registration(db, username, password, current_app.config["PASSWORD_SALT"])


@bp.route("/api/account/add-user-to-queue", methods = ["POST"])
@token_required
def add_user_to_register_queue():
    db = current_app.config["MONGODB_INST"]
    
    return handlers.process_add_user_to_queue(
        db,
        request.json.get("username", None),
        request.json.get("rights", None),
        request.current_user.get("rights", None),
        )