from library.jwtokens import token_required
from flask import (
    Blueprint,
    current_app,
    )



bp = Blueprint("api-common", __name__)


@bp.route("/api/server/info", methods = ["POST"])
@token_required
def get_server_info():
    db = current_app.extensions["postgresdb"]
    server_name = db.fetchone("SELECT data FROM settings WHERE key = 'server-name'")
    if not server_name:
        server_name = "Exworlds server"
    else:
        server_name = server_name._asdict()["data"]["value"]
    
    return {"server_name": server_name, "server_version": current_app.config["version"]}, 200