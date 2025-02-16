import re

point_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_\-]*)")
first_point_re = re.compile(r"^[a-z]{2}:(?P<pack>[A-Za-z_][A-Za-z0-9_\-]*):?(?P<addon>[A-Za-z_][A-Za-z0-9_\-]*)?")

class ParsePathException(Exception):
    pass

class VerifyPathException(Exception):
    pass

class IntegrityPathException(Exception):
    pass


class ContentPath:
    def __init__(self, path: str, category: str = None):
        self.category, self.pack, self.addon, self.table, self.note = ContentPath.parse(path, category)
        
        if self.addon:
            self.fpack = self.category + self.pack + ":" + self.addon
        else:
            self.fpack = self.category + self.pack
        
        self.availables = {
            "pack": True if self.pack else False,
            "addon": True if self.addon else False,
            "table": True if self.table else False,
            "note": True if self.note else False,
        }
    
    def to_str(self):
        points = [self.fpack, self.table, self.note]
        points = [p for p in points if p != None]
        return ".".join(points)
    
    @property
    def to_pack(self):
        return self.fpack
    
    @property
    def to_table(self):
        return self.fpack + self.table
    
    @property
    def to_note(self):
        return self.fpack + self.table + self.note
    
    def __repr__(self):
        return f"<CPath {self.to_str()}>"
    
    @staticmethod
    def parse(path: str, spare_ctg: str = None):
        available_categories = ["gc:", "ip:", "wo:", "ag:"]
        if not path[:3] in available_categories and spare_ctg in available_categories:
            path = spare_ctg + path
        
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
                    return VerifyPathException(f"Point have a wrong format {point}")
            if index == 0:
                if not re.fullmatch(first_point_re, point):
                    return VerifyPathException(f"First point have a wrong format {point}")
                groups = re.match(first_point_re, point)
                pack = groups["pack"]
                addon = groups["addon"]
            elif index == 1:
                table = point
            elif index == 2:
                note = point
            else:
                return ParsePathException(f"More points when expected. Expected 3 or less, given {len(path.solit('.'))}")
        return (category, pack, addon, table, note)

    @classmethod
    def safety(cls, path: str, spare_ctg: str = None, expected: str = None):
        try:
            path_object = cls(path, spare_ctg)
            if expected and not path_object.availables[expected]:
                raise IntegrityPathException("Expectend end point is not available.")
            return path_object
        except (ParsePathException, VerifyPathException, IntegrityPathException):
            return None



if __name__ == "__main__":
    print(ContentPath("hello:world.pack.sook"))
    print(ContentPath("hello").note_available)