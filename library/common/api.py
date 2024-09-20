from flask import (
    Blueprint,
    current_app,
    )



bp = Blueprint("api-common", __name__)


@bp.route("/api/server/info", methods = ["POST"])
def get_server_info():
    db = current_app.config["MONGODB_INST"]
    server_name = db.users.find_one({"username": "Server"}, {"info": 1}).get("server-name", "Undefined")
    return {"server_name": server_name}, 200