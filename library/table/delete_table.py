from library import utils
from typing import Union



def process(db, data: dict, sender: dict) -> bool:
    if not data.get("path"):
        return {"msg": "Wrong path."}, 401
    
    table = utils.get_by_path(db, data)
    pack_path = utils.path_back(data["path"])
    pack = utils.get_by_path(db, pack_path)
    
    if not pack or not table:
        return {"msg": "Table or pack not found."}, 401
    
    existed_rights = {"delete-table", "any-delete", "server-admin"}.intersection(sender["rights"])
    if sender["uid"] not in [pack["owner"], *pack["redactors"]] and not existed_rights:
        return {"msg": "You can't do that."}, 401

    db.execute("DELETE FROM tables WHERE path = %s", (table["path"],))
    
    return {"msg": "Table deletion complete"}, 200