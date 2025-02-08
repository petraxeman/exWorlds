from library.table import upload, get_tables, delete_table
from library.jwtokens import token_required
from flask import (
    Blueprint,
    request,
    current_app
    )

bp = Blueprint("api-table", __name__)



@bp.route("/api/tables/upload", methods = ["POST"])
@token_required
def talbe_upload():
    db = current_app.extensions["postgresdb"]
    return upload.process(db, request.json, request.current_user)


@bp.route("/api/tables/get-by-pack", methods = ["POST"])
@token_required
def get_table_by_pack():
    db = current_app.extensions["postgresdb"]
    return get_tables.by_pack(db, request.json, request.current_user)


@bp.route("/api/tables/get", methods = ["POST"])
@token_required
def get_table():
    db = current_app.extensions["postgresdb"]
    return get_tables.specific(db, request.json, request.current_user)


@bp.route("/api/tables/get-hash", methods = ["POST"])
@token_required
def get_table_hash():
    db = current_app.extensions["postgresdb"]
    return get_tables.hash(db, request.json, request.current_user)
    

@bp.route("/api/tables/delete", methods = ["POST"])
@token_required
def delete_table():
    db = current_app.extensions["postgresdb"]
    return delete_table.process(db, request.json, request.current_user)
    