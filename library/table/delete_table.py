from library import utils, contpath
from typing import Union



def process(db, data: dict, sender: dict) -> bool:
    path = contpath.ContentPath.safety(data.get("path", ""), "gc:", "pack")
    if not path:
        return {"msg": "Wrong path."}, 401
    
    table = db.fetchone("SELECT * FROM tables WHERE path = %s", (path.to_table))
    
    if table["system_table"]:
        return {"msg": "You can't do that."}, 401
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack))
    
    if not pack or not table:
        return {"msg": "Table or pack not found."}, 401
    
    if not utils.verify_access(sender["uid"], sender["rights"], {"delete-table", "any-delete", "server-admin"}, (pack["owner"], *pack["redactors"])):
        return {"msg": "You can't do that."}, 401

    db.execute("DELETE FROM tables WHERE path = %s", (path.to_table,))
    notes_count = db.fetchone("SELECT count(*) FROM notes WHERE starts_with(path, %s)", (path.to_table,))
    db.execute("DELETE FROM notes WHERE starts_with(path, %s)", (path.to_table,))
    
    return {"msg": f"Table {path.to_table} deletion complete. Also deleted {notes_count} notes."}, 200