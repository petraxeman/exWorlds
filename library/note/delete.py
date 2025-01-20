from typing import Union
from library import utils



def process(db, data: dict, sender: dict) -> Union[tuple, int]:
    if not data.get("path"):
        return {"msg": "Wrong path"}, 401
    
    note = db.fetchone("SELECT * FROM notes WHERE path = %s", (data["path"],))
    if not note:
        return {"msg": "Note not found"}, 401
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (utils.path_back(data["path"]),))
    
    existed_rights = {"server-admin", "any-create"}.intersection(sender["rights"])
    if sender["uid"] not in [pack["owner"], *pack["redactors"]] and not existed_rights:
        return {"msg": "You can't do that"}, 401
    
    db.execute("DELETE FROM notes WHERE path = %s", (note["path"],))
    
    return {"msg": "Note delete success"}