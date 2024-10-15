from library.pack import handlers
from library.jwtokens import token_required
from flask import (
    Blueprint,
    request,
    current_app
    )

bp = Blueprint("api-pack", __name__)



@bp.route("/pack/upload", methods = ["POST"])
@token_required
def pack_upload():
    db = current_app.config["MONGODB_INST"]
    return handlers.process_pack_upload(db, request.json, request.current_user)

@bp.route("/pack/get", methods = ["POST"])
@token_required
def get_system():
    db = current_app.config["MONGODB_INST"]
    return handlers.process_pack_get(db, request.json)


@bp.route("/game-system/get-hash", methods = ["POST"])
@token_required
def get_system_hash():
    db = current_app.config["MONGODB_INST"]
    codename = request.json.get("codename", "")
    
    if not codename:
        return {"msg": "Undefined system"}, 401
    
    existed_game_system = db.structs.find_one({"type": "game-system", "codename": codename})
    if not existed_game_system:
        return {"msg": "Undefined system"}, 401
    
    return {"hash": existed_game_system["hash"]}, 200


@bp.route("/game-system/get-systems-by-page", methods = ["POST"])
@token_required
def get_systems():
    db = current_app.config["MONGODB_INST"]
    page = int(request.json.get("page", 1))
    systems = db.structs.find({"type": "game-system"}).skip(10 * (page - 1)).limit(10)
    codenames = [el["codename"] for el in systems]
    return {"systems": codenames}, 200


@bp.route("/game-systems/get-count", methods = ["POST"])
@token_required
def get_systems_count():
    db = current_app.config["MONGODB_INST"]
    count = db.structs.count_documents({"type": "game-system"})
    return {"count": count}


@bp.route("/game-systems/delete", methods = ["POST"])
@token_required
def delete_system():
    db = current_app.config["MONGODB_INST"]
    
    if not request.json.get("codename", False):
        return {"msg": "Undefined codename"}, 401

    result = handlers.delete_game_system(db, request.json.get("codename"), request.current_user)

    if not result:
        return {"msg": "Somthing went wrong. Try again later"}, 401
    
    return {"msg": f"System <{request.json.get("codename")}> deleted."}, 200