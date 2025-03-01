from library import utils, contpath
from typing import Union



def process(db, data: dict, sender: dict) -> Union[dict, int]:
    path = contpath.ContentPath.safety(data.get("path", ""), "gc:", "table")
    if not path:
        return {"msg": "Wrong path."}, 401
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))
    
    if not pack:
        return {"msg": "Wrong path"}, 401
    
    if not utils.verify_access(sender["uid"], sender["rights"], {"server-admin"}, (pack["owner"], *pack["redactors"],)):
        return {"msg": "You can't do that"}, 401
    
    data["path"] = path.to_table
    data["owner"] = sender["uid"]
    if origin := db.fetchone("SELECT * FROM tables WHERE path = %s", (path.to_table,)):
        if origin["system_table"]:
            return {"msg": "You can't do that"}, 401
        table = utils.build_table(data, origin)
        db.execute("UPDATE tables SET name = %(name)s, common = %(common)s, data = %(data)s, hash = %(hash)s WHERE path = %(path)s", table)
        return {"msg": "Updating table success", "hash": table["hash"]}
    else:
        table = utils.build_table(data)
        db.execute("INSERT INTO tables (name, path, owner, common, data, hash) VALUES (%(name)s, %(path)s, %(owner)s, %(common)s, %(data)s, %(hash)s)", table)
        return {"msg": "Creating table success", "hash": table["hash"]}