import datetime
import io
import uuid
from library.jwtokens import token_required
from flask import (
    Blueprint,
    request,
    current_app,
    send_file
    )

bp = Blueprint("api-images", __name__)



@bp.route("/api/image/upload", methods = ["POST"])
@token_required
def upload_image():
    db = current_app.extensions['postgresdb']
    current_user = request.current_user
    
    if 'image' not in request.files:
        return {"msg": "No file part"}, 401
    
    file = request.files['image']
    if file.filename == '':
        return {"msg": "No selected file"}, 401
    
    if file.filename.split(".")[-1] not in ["webp", "gif"]:
        return {"msg": "Wrong extension"}, 401

    uid = current_user["uid"]
    image_date = datetime.datetime.now().strftime("%H%M%d%m%y")
    image_uuid = str(uuid.uuid4())
    image_name = f"codename-{uid}-{image_date}-{image_uuid}.webp"

    image_bytes = request.files['image'].read()
    
    db.execute("INSERT INTO images (filename, codename, owner, data) VALUES (%s, %s, %s, %s)", (file.filename, image_name, uid, image_bytes))
    return {"filename": image_name}, 200


@bp.route("/api/image/download", methods = ["POST"])
@token_required
def download_image():
    db = current_app.extensions['postgresdb']
    current_user = request.current_user
    
    filename = request.json.get("filename")
    image_path = request.json.get("path", "/")
    if filename.startswith("codename-"):
        image = db.fetchone("SELECT filename, data FROM images WHERE codename = %s", (filename,))
    elif filename != '':
        image = db.fetchone("SELECT filename, data FROM images WHERE owner = %s AND path = %s AND filename = %s", (current_user['uid'], image_path, filename))
    else:
        return {"msg": "Wrong filename"}, 401

    if image is None:
        return {"msg": "File does not exist"}, 401

    return send_file(io.BytesIO(bytes(image['data'])), mimetype="image/webp", download_name = image["filename"]), 200


@bp.route("/api/image/delete", methods = ["POST"])
@token_required
def delete_image():
    db = current_app.extensions['postgresdb']
    current_user = request.current_user

    filename = request.json.get("filename")
    image_path = request.json.get("path", "/")
    if filename.startswith("codename-"):
        image = db.fetchone("SELECT codename, owner FROM images WHERE codename = %s", (filename,))
    elif filename != '':
        image = db.fetchone("SELECT codename, owner FROM images WHERE owner = %s AND path = %s AND filename = %s", (current_user['uid'], image_path, filename))
    else:
        return {"msg": "Wrong filename"}, 401

    if image is None:
        return {"msg": "File does not exist"}, 401
    
    if current_user["uid"] != image["owner"] and (current_user["role"] not in ["admin", "server-admin"]):
        return {"msg": "You can't do that"}, 401
    
    db.execute("DELETE FROM images WHERE codename = %s", (image["codename"],))

    return {"msg": f"File deleted <{filename}>"}, 200