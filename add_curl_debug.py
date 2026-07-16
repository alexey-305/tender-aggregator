c = open("app/services/parsers/eis/client.py", "r", encoding="utf-8").read()
c = c.replace("if self.curl_binary:", "print(\"USING CURL\")\n        if self.curl_binary:")
open("app/services/parsers/eis/client.py", "w", encoding="utf-8").write(c)
print("OK")