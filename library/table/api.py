from library.table import handlers
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
    return handlers.process_table_upload(db, request.json, request.current_user)


@bp.route("/api/tables/get", methods = ["POST"])
@token_required
def get_table():
    db = current_app.extensions["postgresdb"]
    return handlers.process_table_get(db, request.json)


@bp.route("/api/tables/get-hash", methods = ["POST"])
@token_required
def get_table_hash():
    db = current_app.extensions["postgresdb"]
    return handlers.process_table_get_hash(db, request.json)
    

@bp.route("/api/tables/delete", methods = ["POST"])
@token_required
def delete_table():
    db = current_app.extensions["postgresdb"]
    return handlers.proccess_table_deletion(db, request.json, request.current_user)
    