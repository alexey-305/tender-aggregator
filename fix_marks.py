c = open("frontend/src/components/TenderCard.jsx", "r", encoding="utf-8").read()
old = "if (tenderMarks.find(m => m.id === mark.id)) {\n      newMarks = tenderMarks.filter(m => m.id !== mark.id);\n    } else {\n      newMarks = [...tenderMarks, mark];\n    }"
new = "if (tenderMarks.find(m => m.id === mark.id)) {\n      newMarks = [];\n    } else {\n      newMarks = [mark];\n    }"
c = c.replace(old, new)
open("frontend/src/components/TenderCard.jsx", "w", encoding="utf-8").write(c)
print("OK")