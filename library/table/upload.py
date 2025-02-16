from library import utils, contpath
from typing import Union



def process(db, data: dict, sender: dict) -> Union[dict, int]:
    path = contpath.ContentPath(data.get("path", ""), "gc:", "table")
    if not path:
        return {"msg": "Wrong path."}, 401
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))
    
    if not pack:
        return {"msg": "Wrong path"}, 401
    
    if not utils.verify_access(sender["uid"], sender["rights"], {"server-admin"}, (pack["owner"], *pack["redactors"],)):
        return {"msg": "You can't do that"}, 401
    
    data["owner"] = sender["uid"]
    if origin := db.fetchone("SELECT * FROM tables WHERE path = %s", (path.to_table,)):
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
            "search-fields": new.get("common", {}).get("search-fields", []) or origin.get("common", {}).get("search-fields", ["name"]),
            "short-view":    new.get("common", {}).get("short-view")        or origin.get("common", {}).get("short-view", ["name"]),
            "table-icon":    new.get("common", {}).get("table-icon")        or origin.get("common", {}).get("table-icon", "opened-book"),
            "table-display": new.get("common", {}).get("search-display")    or origin.get("common", {}).get("search-display", "list"),
        },
        "data": {
            "properties": new.get("data", {}).get("properties") or origin.get("data", {}).get("properties", {}),
            "macros":     new.get("data", {}).get("macros")     or origin.get("data", {}).get("macros", {}),
            "schema":     new.get("data", {}).get("schema")     or origin.get("data", {}).get("schema", []),
            "fields":     new.get("data", {}).get("fields")     or origin.get("data", {}).get("fields", {})
        }
    }
    
    table["hash"] = utils.get_hash(str(table))
    return table