import winhttp
import sys

# Пытаемся подключиться к int44.zakupki.gov.ru через WinHTTP (использует системное хранилище сертификатов + КриптоПро)
try:
    session = winhttp.WinHttpSession()
    req = winhttp.WinHttpRequest(session)
    req.open("GET", "https://int44.zakupki.gov.ru/eis-integration/services/getDocsLE?wsdl")
    req.send()
    print("Status:", req.status)
    print(req.response_text[:500])
except Exception as e:
    print("Error:", e)