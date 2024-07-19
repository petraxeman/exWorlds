import re


t = re.compile("[a-z\-]+")

print(t.fullmatch("asd"))
print(t.fullmatch("asd--"))
print(t.fullmatch("asd---------------asd"))
print(t.fullmatch("asdD \nasd"))
print(t.fullmatch("asd1"))