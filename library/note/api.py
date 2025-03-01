from library.note import upload, delete, search
from library.jwtokens import token_required
from library import utils
from flask import (
    Blueprint,
    request,
    current_app
    )

bp = Blueprint("api-note", __name__)



@bp.route("/api/notes/upload", methods = ["POST"])
@token_required
def note_upload():
    db = current_app.extensions["postgresdb"]
    return upload.process(db, request.json, request.current_user)


@bp.route("/api/notes/delete", methods = ["POST"])
@token_required
def note_delete():
    db = current_app.extensions["postgresdb"]
    return delete.process(db, request.json, request.current_user)


@bp.route("/api/notes/get", methods = ["POST"])
@token_required
def note_get():
    db = current_app.extensions["postgresdb"]
    return search.by_path(db, request.json, request.current_user)


@bp.route("/api/notes/search", methods = ["POST"])
@token_required
def note_search():
    db = current_app.extensions["postgresdb"]
    return search.by_query(db, request.json, request.current_user)