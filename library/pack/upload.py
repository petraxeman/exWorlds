import hashlib
from library.search_utils import make_ngram
from library import utils, contpath
from typing import Union




def process(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("path") or not data.get("image-name"):
        return {"msg": "Undefined pack or undefined poster."}, 401
    
    path = contpath.ContentPath.safety(data.get("path", ""))
    if not path:
        return {"msg": "Wrong path."}, 401
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))

    if pack:
        return update_existed(db, data, pack, path.to_pack, sender)
    else:
        return upload_new(db, data, path, sender)


def update_existed(db, data, pack, str_path, sender):
    if "server-admin" not in sender["rights"] and pack["owner"] != sender["uid"]:
        return {"msg": "You can't do that."}, 401
    
    new_pack = build_pack(data, pack)
    db.execute("UPDATE packs SET name = %s, image_name = %s, hash = %s WHERE path = %s",
                (new_pack["name"], new_pack["image-name"], new_pack["hash"], str_path))
    
    return {"hash": new_pack["hash"]}, 200


def upload_new(db, data: dict, path: contpath.ContentPath, sender: dict) -> Union[dict, int]:
    if path.points["category"] == "gc:":
        rules = utils.build_table({"name": "Rules", "path": path.to_pack + ".rules"})
        macros = utils.build_table({"name": "Macros", "path": path.to_pack + ".macros"})
        
        db.execute("INSERT INTO tables (system_table, changeable_schema, name, path, owner, common, data, hash) VALUES \
            (true, true, %(name)s, %(path)s, %(owner)s, %(common)s, %(data)s, %(hash)s)", rules)
        
        db.execute("INSERT INTO tables (system_table, name, path, owner, common, data, hash) VALUES \
            (true, %(name)s, %(path)s, %(owner)s, %(common)s, %(data)s, %(hash)s)", macros)
        
    existed_rights = {"create-pack", "any-create", "server-admin"}.intersection(sender["rights"])
    if not existed_rights:
        return {"msg": "You can't do that."}, 401
    
    new_pack = build_pack(data, {})
    db.execute("INSERT INTO packs (name, image_name, path, owner, hash) VALUES (%s, %s, %s, %s, %s)",
                (new_pack["name"], new_pack["image-name"], path.to_pack, sender["uid"], new_pack["hash"]))
    
    return {"hash": new_pack["hash"]}, 200


def build_pack(new: dict, origin: dict = {}) -> dict:
    pack = {
        "name": new.get("name") or origin.get("name"),
        "image-name": new.get("image-name") or origin.get("image-name"),
        "path": origin.get("path"),
        "readctors": new.get("redactors") or origin.get("redactors"),
    }
    pack["search-field"] = make_ngram(pack["name"], 3, 4)
    pack["hash"] = get_pack_hash(pack)
    
    return pack


def get_pack_hash(instance: dict) -> str:
    return hashlib.md5(
        f'{instance["name"]} {instance["image-name"]}'.encode()).hexdigest()