import re, copy

point_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_\-]*)")
first_point_re = re.compile(r"^[a-z]{2}:(?P<pack>[A-Za-z_][A-Za-z0-9_\-]*):?(?P<addon>[A-Za-z_][A-Za-z0-9_\-]*)?")

class ParsePathException(Exception):
    pass

class VerifyPathException(Exception):
    pass

class IntegrityPathException(Exception):
    pass



class ContentPath:
    def __init__(self, path: str, spare_ctg: str = None):
        category, pack, addon, table, note = ContentPath.parse(path, spare_ctg)
        
        self.points = {
            "category": category or False,
            "pack": pack or False,
            "addon": addon or False,
            "table": table or False,
            "note": note or False,
        }
        
        if self.points["addon"]:
            self.points["fpack"] = self.points["category"] + self.points["pack"] + ":" + self.points["addon"]
        else:
            self.points["fpack"] = self.points["category"] + self.points["pack"]
    
    def to_str(self):
        points = [self.points["fpack"], self.points["table"], self.points["note"]]
        points = [p for p in points if p]
        return ".".join(points)
    
    def duplicate(self):
        return copy.deepcopy(self)
    
    @property
    def to_pack(self):
        return self.points["fpack"]
    
    @property
    def to_table(self):
        return self.points["fpack"] + "." + self.points["table"]
    
    @property
    def to_note(self):
        return self.points["fpack"] + "." + self.points["table"] + "." + self.points["note"]
    
    def __repr__(self):
        return f"<CPath {self.to_str()}>"
    
    @staticmethod
    def parse(path: str, spare_ctg: str = None):
        available_categories = ["gc:", "ip:", "wo:", "ag:"]
        if not path[:3] in available_categories:
            raise VerifyPathException(f"Unexpected path category {path[:3]}")
        
        if path[:3] in available_categories:
            category = path[:3]
            if spare_ctg and category != spare_ctg:
                raise VerifyPathException(f"Expected {spare_ctg}, but got {path[:3]}")
        else:
            raise ParsePathException(f"Undefined path category. Possible {available_categories}, got {path[:3]}")
        
        pack = ''
        addon = None
        table = None
        note = None
        for index, point in enumerate(path.split(".")):
            if index != 0:
                if not re.fullmatch(point_re, point):
                    raise VerifyPathException(f"Point have a wrong format {point}")
            if index == 0:
                if not re.fullmatch(first_point_re, point):
                    raise VerifyPathException(f"First point have a wrong format {point}")
                groups = re.match(first_point_re, point)
                pack = groups["pack"]
                addon = groups["addon"]
            elif index == 1:
                table = point
            elif index == 2:
                note = point
            else:
                raise ParsePathException(f"More points when expected. Expected 3 or less, given {len(path.solit('.'))}")
        return (category, pack, addon, table, note)

    @classmethod
    def safety(cls, path: str, spare_ctg: str = None, expected: str = None):
        try:
            path_object = cls(path, spare_ctg)
            if expected and not path_object.points[expected]:
                raise IntegrityPathException("Expectend end point is not available.")
            return path_object
        except (ParsePathException, VerifyPathException, IntegrityPathException):
            return None



if __name__ == "__main__":
    print(ContentPath("hello:world.pack.sook"))
    print(ContentPath("hello").note_available)