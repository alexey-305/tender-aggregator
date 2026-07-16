c = open("frontend/src/components/TenderList.jsx", "r", encoding="utf-8").read()
old = '&price_to=" + (activeKey.price_to || "")'
new = '&price_to=" + (activeKey.price_to || "") + "&platforms=" + (activeKey.platforms || "") + "&methods=" + (activeKey.methods || "")'
c = c.replace(old, new)
open("frontend/src/components/TenderList.jsx", "w", encoding="utf-8").write(c)
print("OK")