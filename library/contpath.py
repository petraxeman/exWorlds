import re

point_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_\-]*)")
first_point_re = re.compile(r"^(?P<pack>[A-Za-z_][A-Za-z0-9_\-]*):?(?P<addon>[A-Za-z_][A-Za-z0-9_\-]*)?")

class ParsePathException(Exception):
    pass

class VerifyPathException(Exception):
    pass



class ContentPath:
    def __init__(self, path: str):
        self.pack, self.addon, self.table, self.note = ContentPath.parse(path)
        
        if self.addon:
            self.fpack = self.pack + ":" + self.addon
        else:
            self.fpack = self.pack
        
        self.pack_exists = True if self.pack else False
        self.addon_exists = True if self.addon else False
        self.table_exists = True if self.table else False
        self.note_exists = True if self.note else False
    
    @property
    def str_path(self):
        points = [self.fpack, self.table, self.note]
        points = [p for p in points if p != None]
        return ".".join(points)
    
    def __repr__(self):
        
        return f"<CPath {self.str_path}>"
    
    @staticmethod
    def verify(path: str):
        for index, point in enumerate(path.split(".")):
            if index == 0:
                if not re.fullmatch(first_point_re, point):
                    return VerifyPathException()
            else:
                if not re.fullmatch(point_re, point):
                    return VerifyPathException()
    
    @staticmethod
    def parse(path: str, verify: bool = True):
        if verify:
            ContentPath.verify(path)
        pack = ''
        addon = None
        table = None
        note = None
        for index, point in enumerate(path.split(".")):
            if index == 0:
                groups = re.match(first_point_re, point)
                pack = groups["pack"]
                addon = groups["addon"]
            elif index == 1:
                table = point
            elif index == 2:
                note = point
            else:
                return ParsePathException
        return (pack, addon, table, note)


if __name__ == "__main__":
    print(ContentPath("hello:world.pack.sook"))
    print(ContentPath("hello").note_exists)