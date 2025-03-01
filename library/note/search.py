from typing import Union
from library import utils, contpath



def by_path(db, data: dict, sender: dict) -> Union[tuple, int]:
    if not data.get("path-list", []):
        return {"msg": "Pathes undefined."}, 401
    
    pack_cache = {}
    notes = []
    
    for path in data.get("path-list"):
        path = contpath.ContentPath.safety(path, "gc:", "note")
        if not path:
            continue

        if path.to_note not in pack_cache.keys():
            pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_pack,))
            if pack:
                if pack["hidden"]:
                    if sender["uid"] not in [pack["owner"], *pack["redactors"]] and "server-admin" in sender["rights"]:
                        pack_cache[pack["path"]] = False
                    else:
                        pack_cache[pack["path"]] = True
                else:
                    pack_cache[pack["path"]] = True
            else:
                pack_cache[path.to_pack] = False
        
        if pack_cache[path.to_pack] == True:
            notes.append(db.fetchone("SELECT * FROM notes WHERE path = %s", (path.to_note,)))        
    
    if not notes:
        return {"msg": "Notes not found."}, 401
    
    return {"notes": notes}


#
# Search request format:
# {
#    "common": {
#      "page": 1                              # What page of content
#      "source": "gc:game-system.table"       # What table is used for search
#    },
#    "filters": [
#      {}
#    ]

#
# Filter format = {"value": "xxx", "codename": "xxx"}
#
def by_query(db, data: dict, sender: dict) -> Union[tuple, int]:
    page = int(data.get("common", {}).get("page", 1))
    
    path = contpath.ContentPath.safety(data.get("common", {}).get("source", ""), "gc:", "table")
    if not path:
        return {"Source table is undefined"}, 401
    
    args = {"user_uid": sender["uid"], "starts_with": path.to_table, "page": page, "limit": 10, "offset": 10 * (page - 1)}
    
    filters = data.get("filters", [])
    
    pack = db.fetchone(f"SELECT * FROM packs WHERE path = %s LIMIT 1;", (path.to_pack,))
    if not pack:
        return {"msg": "Pack not found."}, 401

    if pack["hidden"]:
        if not utils.verify_access(
            sender["uid"], sender["rights"],
            {"server-admin"},
            [pack["owner"], *pack["redactors"]]
            ):
            return {"msg": "Pack not found."}, 401

    table = db.fetchone("SELECT * FROM tables WHERE path = %s LIMIT 1;", (path.to_table,))
    
    query = """SELECT path FROM notes WHERE """
    
    comparisons_queries = []
    comparisons_args = {}
    for index, filter in enumerate(filters):
        if filter["codename"] in ("~full_text_search",):
            continue
        
        comparisons_args[f"f{index}_codename"] = filter["codename"]
        
        match table["data"]["fields"][filter["codename"]]["type"]:
            case "integer" | "float" | "dice":
                comparisons_args[f"f{index}_check"] = filter.get("check", "avg")
                comparisons_args[f"f{index}_min"] = filter.get("min", 0)
                comparisons_args[f"f{index}_max"] = filter.get("max", 10000)
                
                comparison_value = f"(fields->%(f{index}_codename)s->>%(f{index}_check)s)::int"
                comparisons_queries.append(f"( {comparison_value} > %(f{index}_min)s )")
                comparisons_queries.append(f"( {comparison_value} < %(f{index}_max)s )")
            case "string" | "paragraph":
                comparisons_args[f"f{index}_value"] = filter["value"]
                comparisons_queries.append(f"(data->'fields'->%(f{index}_codename)s->>'value')::TEXT LIKE %(f{index}_value)s")
            case "bool":
                comparisons_queries.append(f"(data->'fields'->%(f{index}_codename)s->>'value')::BOOLEAN = %(f{index}_value)s")

    query += " AND ".join(comparisons_queries)
    args.update(comparisons_args)
    query += " LIMIT %(limit)s OFFSET %(offset)s;"
    
    notes = db.fetchall(query, args)
    notes = [note["path"] for note in notes]
    
    return {"path-list": notes}, 200