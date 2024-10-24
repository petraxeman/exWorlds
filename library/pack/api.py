from library.pack import handlers, get_by_page, upload
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
    return upload.process(db, request.json, request.current_user)


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
    return get_by_page.process(db, request.json, request.current_user)


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


@bp.route("/pack/toggle/hide", methods = ["POST"])
@token_required
def toggle_hiden():
    db = current_app.config["MONGODB_INST"]
    return handlers.toggle(db, request.json, request.current_user, "hidden")


@bp.route("/pack/toggle/freeze", methods = ["POST"])
@token_required
def toggle_freeze():
    db = current_app.config["MONGODB_INST"]
    return handlers.toggle(db, request.json, request.current_user, "freezed")


@bp.route("/pack/toggle/favorite", methods = ["POST"])
@token_required
def toggle_favorite():
    return handlers.toggle_list(current_app.config["MONGODB_INST"], request.json, request.current_user, "favorites")


@bp.route("/pack/toggle/like", methods = ["POST"])
@token_required
def toggle_like():
    return handlers.toggle_list(current_app.config["MONGODB_INST"], request.json, request.current_user, "likes")