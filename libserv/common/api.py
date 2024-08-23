from flask import (
    Blueprint,
    current_app,
    )



bp = Blueprint("api-common", __name__)


@bp.route("/api/server/info", methods = ["POST"])
def get_server_info():
    return {"server_name": current_app.config["LSERVER_NAME"]}, 200