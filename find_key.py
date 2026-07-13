import PyKCS11 as pkcs11
lib = pkcs11.PyKCS11Lib()
lib.load('C:/Program Files (x86)/stunnel/engines/rtpkcs11ecp.dll')
for slot in lib.getSlotList():
    try:
        info = lib.getTokenInfo(slot)
        print(f'Slot {slot}: {info.label}')
    except:
        continue
    try:
        session = lib.openSession(slot)
        session.login('12345678')
        for obj in session.findObjects([(pkcs11.CKA_CLASS, pkcs11.CKO_PRIVATE_KEY)]):
            attr = session.getAttributeValue(obj, [pkcs11.CKA_ID, pkcs11.CKA_LABEL])
            print(f'  Key: {bytes(attr[0]).hex()} - {bytes(attr[1]).decode(errors="replace")}')
        for obj in session.findObjects([(pkcs11.CKA_CLASS, pkcs11.CKO_CERTIFICATE)]):
            attr = session.getAttributeValue(obj, [pkcs11.CKA_ID, pkcs11.CKA_LABEL, pkcs11.CKA_SUBJECT])
            print(f'  Cert: {bytes(attr[0]).hex()} - {bytes(attr[2]).decode(errors="replace")}')
        session.logout()
        session.closeSession()
    except Exception as e:
        print(f'  Error: {e}')