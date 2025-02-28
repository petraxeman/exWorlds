from typing import Union
from library import utils, contpath, search_utils



def process(db, data: dict, sender: dict) -> Union[tuple, int]:
    path = contpath.ContentPath.safety(data.get("path", ""))
    if not path:
        return {"msg": "Wrong path."}, 401
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))
    
    if not utils.verify_access(
        sender["uid"], 
        sender["rights"], 
        {"server-admin", "any-create"}, 
        (pack["owner"], *pack["redactors"])):
        return {"msg": "You can't do that"}, 401
    
    if db_note := db.fetchone("SELECT * FROM notes WHERE path = %s", (path.to_note,)):
        note = build_note(data, db_note)
        db.execute("UPDATE notes SET fields = %s, schema = %s WHERE path = %s", 
                   (note["fields"], note["schema"], path.to_pack))
    else:
        note = build_note(data)
        db.execute("INSERT INTO notes (owner, path, fields, schema, hash) VALUES (%s, %s, %s, %s, %s)",
                   (sender["uid"]), path.to_note, note["fields"], note["schema"], note["hash"])
    return {"msg": "Note upload success"}


def build_note(new: dict, origin: dict = {}):
    new_note = {
        "owner": origin.get("owner") or new.get("owner"),
        "path": origin.get("path") or new.get("path"),
        "fields": new.get("fields") or origin.get("fields"),
        "schema": new.get("schema") or origin.get("schema"),
    }
    new_note["hash"] = utils.get_hash(str(new_note["fields"]) + " " + str(new_note["schema"]))
    
    new_note["search_field"] = ""
    for field in new_note["fields"]:
        if new_note[field]["type"] in ("string", "text",):
            new_note += new_note[field]["value"]
    new_note["search_field"] = search_utils.make_ngram(new_note["search_field"], 3, 4)
    
    return new_note