from library import utils
from typing import Union



def process(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("path"):
        return {"msg": "Undefind operation"}, 401
    
    parent_pack_path = utils.table_to_pack(data["path"])
    parent_pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (parent_pack_path,))
    
    if not parent_pack:
        return {"msg": "Wrong path"}, 401
    
    if sender["uid"] not in [parent_pack["owner"], *parent_pack["redactors"]] and "server-admin" not in sender["rights"]:
        return {"msg": "You can't do that"}, 401
    
    data["owner"] = sender["uid"]
    if origin := db.fetchone("SELECT * FROM tables WHERE path = %s", (data["path"],)):
        table = build_table(data, origin)
        db.execute("UPDATE tables SET name = %(name)s, common = %(common)s, data = %(data)s, hash = %(hash)s WHERE path = %(path)s", table)
        return {"msg": "Updating table success", "hash": table["hash"]}
    else:
        table = build_table(data)
        db.execute("INSERT INTO tables (name, path, owner, common, data, hash) VALUES (%(name)s, %(path)s, %(owner)s, %(common)s, %(data)s, %(hash)s)", table)
        return {"msg": "Creating table success", "hash": table["hash"]}


def build_table(new: dict, origin: dict = {}) -> dict:
    table = {
        "name": new.get("name") or origin.get("name"),
        "owner": origin.get("owner") or new.get("owner"),
        "path": origin.get("path") or new.get("path"),
        "common": {
            "search-fields": new.get("search-fields", []) or origin.get("search-fields", ["name"]),
            "short-view": new.get("short-view") or origin.get("short-view", ["name"]),
            "table-icon": new.get("table-icon") or origin.get("table-icon", "opened-book"),
            "table-display": new.get("search-display") or origin.get("search-display", "list"),
        },
        "data": {
            "properties": new.get("properties") or origin.get("properties", {}),
            "macros": new.get("macros") or origin.get("macros", {}),
            "schema": new.get("schema") or origin.get("schema", []),
            "fields": new.get("fields") or origin.get("fields", {})
        }
    }
    
    table["hash"] = utils.get_hash(str(table))
    return table