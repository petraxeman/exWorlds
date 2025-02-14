from typing import Union
from library import contpath



def process(db, data: dict, sender: dict) -> Union[dict, int]:
    try:
        path = contpath.ContentPath(data.get("path", ""), "gc:")
    except contpath.ParsePathException:
        return {"msg": "Wrong path."}, 401
    
    options = data.get("options", {})
    
    pack = db.fetchone("SELECT * FROM packs WHERE path = %s", (path.to_str(),))
    if not pack:
        return {"msg": "Pack not found."}, 401
    
    existed_rights = {"delete-pack", "any-delete", "server-admin"}.intersection(sender["rights"])
    if sender["uid"] != pack["owner"] and (not existed_rights):
        return {"msg": "You can't do that."}, 401
    
    delete_pack(db, pack, options)    
    return {"msg": f"System {path.to_str()} deleted."}, 200



def delete_pack(db, pack: dict, options: dict) -> bool:
    if options.get("delete-poster", True):
        db.execute("DELETE FROM images WHERE codename = %s", (pack["image_name"],))
    
    db.execute("DELETE FROM packs WHERE path = %s", (pack["path"],))
    
    db.execute("""
        UPDATE users
        SET lists = jsonb_set(
            jsonb_set(
                lists,
                '{favorites}',
                (lists->'favorites') - %(path_to_remove)s,
                true
            ),
            '{likes}',
            (lists->'likes') - %(path_to_remove)s,
            true
        ) WHERE %(path_to_remove)s = ANY(ARRAY(
            SELECT jsonb_array_elements_text(lists->'favorites')
            UNION
            SELECT jsonb_array_elements_text(lists->'likes')
        ))
    """, {"path_to_remove": pack["path"]})
    
    return True