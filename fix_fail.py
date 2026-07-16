c = open("app/services/parsers/eis/client.py", "r", encoding="utf-8").read()
c = c.replace(""""-sS", "--fail-with-body"""", """"-sS"""")
open("app/services/parsers/eis/client.py", "w", encoding="utf-8").write(c)
print("OK")