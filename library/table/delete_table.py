from library import utils, contpath
from typing import Union



def process(db, data: dict, sender: dict) -> bool:
    if not data.get("path"):
        return {"msg": "Wrong path."}, 401
    
    try:
        path = contpath.ContentPath(data.get("path", ""), "gc:")
    except contpath.ParsePathException:
        return {"msg": "Wrong path."}, 401 
    
    table = db.fetchone("SELECT * FROM tables WHERE path = %s", (path.to_table))
    pack = db.fetchone("SELECT * FROM tables WHERE path = %s", (path.to_pack))
    
    if not pack or not table:
        return {"msg": "Table or pack not found."}, 401
    
    existed_rights = {"delete-table", "any-delete", "server-admin"}.intersection(sender["rights"])
    if sender["uid"] not in [pack["owner"], *pack["redactors"]] and not existed_rights:
        return {"msg": "You can't do that."}, 401

    db.execute("DELETE FROM tables WHERE path = %s", (table["path"],))
    
    return {"msg": "Table deletion complete"}, 200