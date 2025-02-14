from library.pack import handlers, get_by_page, upload, delete
from library.jwtokens import token_required
from library import utils
from flask import (
    Blueprint,
    request,
    current_app
    )

bp = Blueprint("api-pack", __name__)



@bp.route("/api/packs/upload", methods = ["POST"])
@token_required
def pack_upload():
    db = current_app.extensions["postgresdb"]
    return upload.process(db, request.json, request.current_user)


@bp.route("/api/packs/get", methods = ["POST"])
@token_required
def get_system():
    db = current_app.extensions["postgresdb"]
    return handlers.process_pack_get(db, request.json, request.current_user)


@bp.route("/api/packs/get-hash", methods = ["POST"])
@token_required
def get_system_hash():
    db = current_app.extensions["postgresdb"]
    return handlers.process_pack_get_hash(db, request.json, request.current_user)


@bp.route("/api/pack/get-by-page", methods = ["POST"])
@token_required
def get_systems():
    db = current_app.extensions["postgresdb"]
    return get_by_page.process(db, request.json, request.current_user)


@bp.route("/api/packs/get-count", methods = ["POST"])
@token_required
def get_systems_count():
    db = current_app.extensions["postgresdb"]
    
    result = db.fetchone("SELECT count(*) FROM packs WHERE starts_with(path, 'gc:')")
    return {"count": result["count"]}


@bp.route("/api/packs/delete", methods = ["POST"])
@token_required
def delete_system():
    db = current_app.extensions["postgresdb"]
    return delete.process(db, request.json, request.current_user)


@bp.route("/api/packs/toggle/hide", methods = ["POST"])
@token_required
def toggle_hiden():
    db = current_app.extensions["postgresdb"]
    return handlers.toggle(db, request.json, request.current_user, "hidden")


@bp.route("/api/packs/toggle/freeze", methods = ["POST"])
@token_required
def toggle_freeze():
    db = current_app.extensions["postgresdb"]
    return handlers.toggle(db, request.json, request.current_user, "freezed")


@bp.route("/api/packs/toggle/favorite", methods = ["POST"])
@token_required
def toggle_favorite():
    return handlers.toggle_list(current_app.extensions["postgresdb"], request.json, request.current_user, "favorites")


@bp.route("/api/packs/toggle/like", methods = ["POST"])
@token_required
def toggle_like():
    return handlers.toggle_list(current_app.extensions["postgresdb"], request.json, request.current_user, "likes")