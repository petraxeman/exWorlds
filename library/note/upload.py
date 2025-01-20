from typing import Union
from library import utils



def process(db, data: dict, sender: dict) -> Union[tuple, int]:
    if not data.get("path"):
        return {"msg": "Wrong path"}, 401
    
    db_note = db.fetchone("SELECT * FROM notes WHERE path = %s", (data["path"],))
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (utils.path_back(data["path"]),))
    
    existed_rights = {"server-admin", "any-create"}.intersection(sender["rights"])
    if sender["uid"] not in [pack["owner"], *pack["redactors"]] and not existed_rights:
        return {"msg": "You can't do that"}, 401
    
    if db_note:
        note = build_note(data, db_note)
        db.execute("UPDATE notes SET fields = %s, schema = %s", (note["fields"], note["schema"]))
    else:
        note = build_note(data)
        db.execute("INSERT INTO notes (owner, path, fields, schema) VALUES (%s, %s, %s, %s)",
                   (sender["uid"]), note["path"], note["fields"], note["schema"])
    return {"msg": "Note upload success"}


def build_note(new: dict, origin: dict = {}):
    new_note = {
        "owner": origin.get("owner") or new.get("owner"),
        "path": origin.get("path") or new.get("path"),
        "fields": new.get("fields") or origin.get("fields"),
        "schema": new.get("schema") or origin.get("schema"),
    }
    new_note["hash"] = utils.get_hash(str(new_note["fields"]) + " " + str(new_note["schema"]))