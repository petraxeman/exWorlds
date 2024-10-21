from library.pack import handlers
from library.jwtokens import token_required
from library import utils
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
    return handlers.process_pack_get(db, request.json, request.current_user)


@bp.route("/pack/get-hash", methods = ["POST"])
@token_required
def get_system_hash():
    db = current_app.config["MONGODB_INST"]
    return handlers.process_pack_get_hash(db, request.json, request.current_user)


@bp.route("/pack/get-by-page", methods = ["POST"])
@token_required
def get_systems():
    db = current_app.config["MONGODB_INST"]
    return handlers.process_pack_get_by_page(db, request.json)


@bp.route("/pack/get-count", methods = ["POST"])
@token_required
def get_systems_count():
    db = current_app.config["MONGODB_INST"]
    
    if not request.json.get("type", ""):
        return {"msg": "Undefined pack"}, 401

    count = db.packs.count_documents({"type": request.json.get("type", "")})
    return {"count": count}


@bp.route("/pack/delete", methods = ["POST"])
@token_required
def delete_system():
    db = current_app.config["MONGODB_INST"]
    return handlers.process_pack_delete(db, request.json, request.current_user)


@bp.route("/pack/toggle-hidden")
@token_required
def toggle_hiden():
    db = current_app.config["MONGODB_INTS"]
    return handlers.toggle(db, request.json, request.current_user, "hidden")


@bp.route("/pack/toggle-freeze")
@token_required
def toggle_freeze():
    db = current_app.config["MONGODB_INTS"]
    return handlers.toggle(db, request.json, request.current_user, "freezed")


