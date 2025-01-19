from library import utils
from typing import Union



def proccess_table_deletion(db, data: dict, sender: dict) -> bool:
    if not utils.validate_path(data):
        return {"msg": "Wrong path."}, 401
    
    table = utils.get_by_path(db, data)
    pack_path = utils.path_up(data)
    pack = utils.get_by_path(db, pack_path)
    
    if not pack or not table:
        return {"msg": "Table or pack not found."}, 401
    
    existed_rights = {"delete-table", "any-delete", "server-admin"}.intersection(sender["rights"])
    if sender["username"] not in [pack["owner"], *pack["redactors"]] and not existed_rights:
        return {"msg": "You can't do that."}, 401

    db.tables.delete_one(table)
    
    return {"msg": "Table deletion complete"}, 200


