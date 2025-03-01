from typing import Union
from library import utils, contpath, search_utils
import re, numexpr



def process(db, data: dict, sender: dict) -> Union[tuple, int]:
    path = contpath.ContentPath.safety(data.get("path", ""))
    if not path:
        return {"msg": "Wrong path."}, 401
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s LIMIT 1;", (path.to_pack,))
    table = db.fetchone("SELECT * FROM tables WHERE path = %s LIMIT 1;", (path.to_table,))
    
    if not utils.verify_access(
        sender["uid"], 
        sender["rights"], 
        {"server-admin", "any-create"}, 
        (pack["owner"], *pack["redactors"])):
        return {"msg": "You can't do that"}, 401
    
    if db_note := db.fetchone("SELECT * FROM notes WHERE path = %s", (path.to_note,)):
        note = build_note(data, db_note)
        note["fields"] = verify_fields(note["fields"], table)
        db.execute("UPDATE notes SET fields = %s, schema = %s WHERE path = %s", 
                   (note["fields"], note["schema"], path.to_pack))
    else:
        note = build_note(data)
        note["fields"] = verify_fields(note["fields"], table)
        db.execute("INSERT INTO notes (owner, path, search_field, fields, schema, hash) VALUES (%s, %s, %s, %s, %s, %s)",
                   (sender["uid"], path.to_note, note["search_field"], note["fields"], note["schema"], note["hash"],))
    
    return {"msg": "Note upload success"}


def build_note(new: dict, origin: dict = {}):
    new_note = {
        "fields": new.get("fields") or origin.get("fields"),
        "schema": new.get("schema") or origin.get("schema", []),
    }
    new_note["hash"] = utils.get_hash(str(new_note["fields"]) + " " + str(new_note["schema"]))
    
    new_note["search_field"] = ""
    #for field in new_note["fields"]:
    #    if new_note[field]["type"] in ("string", "text",):
    #        new_note += new_note[field]["value"]
    #new_note["search_field"] = search_utils.make_ngram(new_note["search_field"], 3, 4)
    
    return new_note


def verify_fields(fields: dict, table: dict) -> dict:
    nfields = fields.copy()

    for key in nfields:
        finfo = table["data"]["fields"][key]
        match finfo["type"]:
            case "dice":
                if not isinstance(nfields[key], str):
                    continue
                minv, avgv, maxv = parse_dice(nfields[key])
                nfields[key] = {"min": minv, "avg": avgv, "max": maxv, "rec": nfields[key]}
            case "integer":
                value = numexpr.evaluate(str(nfields[key]))
                nfields[key] = {"min": int(value), "avg": int(value), "max": int(value), "rec": nfields[key]}
            case "float":
                value = numexpr.evaluate(str(nfields[key]))
                nfields[key] = {"min": float(value), "avg": float(value), "max": float(value), "rec": nfields[key]}
                
    return nfields


def parse_dice(dice_str: str):
    dice_match = re.findall(r"((?:[1-9][0-9]*)?d\d+|d\d+|\d+|\(|\)|\+|\-|\*|\/)", str(dice_str))
    dice_min = []
    dice_max = []
    for el in dice_match:
        if re.fullmatch(r"((?:[1-9][0-9]*)?d\d+)", str(el)):
            count, size = el.split("d")
            dice_min.append(count)
            dice_max.append(str(int(count) * int(size)))
        elif re.fullmatch(r"\d+", str(el)):
            dice_min.append(el)
            dice_max.append(el)
    print(" ".join(dice_min))
    print(" ".join(dice_max))
    min_value = int(numexpr.evaluate(" ".join(dice_min)))
    max_value = int(numexpr.evaluate(" ".join(dice_max)))
    
    avg_value = (min_value + max_value) / 2
    return min_value, avg_value, max_value