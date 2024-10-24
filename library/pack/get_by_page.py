from typing import Union



def process(db, data: dict, sender: dict) -> Union[dict, int]:
    if not data.get("type", ""):
        return {"msg": "Type undefined"}, 401
    
    pack_type = data.get("type")
    page = int(data.get("page", 1))

    if page < 1:
        return {"msg": "Wrong page range"}, 401
    
    pipeline = []
    
    if data.get("search", ""):
        pipeline.append({"$match": {"$text": {"$search": data.get("search")}}})
    
    pipeline.extend([
        {"$match": {"$expr": {"$eq": ["$type", pack_type]}}},
        {
            "$addFields": {
                "is-favorite": {
                    "$cond": {
                        "if": {"$in": ["$path", sender["lists"]["favorites"]]},
                        "then": True,
                        "else": False,
                    }
                }
            }
        },        
        {
            "$match": {
                "$or": [
                    {"hidden": False},
                    {"$or": [
                        {"owner": sender["username"]}, 
                        {"redactors": {"$in": [sender["username"]]}}
                        ]
                    }
                ]
            }
        },
        {
            "$sort": {
                "text-score": -1,
                "is-favorite": -1,
                "likes": -1
            }
        },
        {"$project": {"_id": 0}},
        {"$limit": 10},
    ])

    if 10 * (page - 1) != 0:
        pipeline.append({"$skip": 10 * (page - 1)})

    path_list = [el["path"] for el in db.packs.aggregate(pipeline)]

    if not path_list:
        return {"msg": "Undefined packs"}
    
    return {"codenames": path_list}, 200