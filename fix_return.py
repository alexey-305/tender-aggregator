path = r'C:\TenderAggregator\frontend\src\components\tenders\TenderList.tsx'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = 'if (marks.length > 0) {\n      return\n    const now = new Date();'
new = 'if (marks.length > 0) return "#ff6b6b";\n    const now = new Date();'

c = c.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print('OK')