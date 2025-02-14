from typing import Union
from library import contpath



def process(db, data: dict, sender: dict) -> Union[tuple, int]:
    if not data.get("path"):
        return {"msg": "Wrong path"}, 401
    
    try:
        path = contpath.ContentPath(data.get("path", ""), "gc:")
    except contpath.ParsePathException:
        return {"msg": "Wrong path."}, 401
    
    note = db.fetchone("SELECT * FROM notes WHERE path = %s", (path.to_note,))
    if not note:
        return {"msg": "Note not found"}, 401
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))
    
    existed_rights = {"server-admin", "any-create"}.intersection(sender["rights"])
    if sender["uid"] not in [pack["owner"], *pack["redactors"]] and not existed_rights:
        return {"msg": "You can't do that"}, 401
    
    db.execute("DELETE FROM notes WHERE path = %s", (path.to_note,))
    
    return {"msg": "Note delete success"}