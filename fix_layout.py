path = r"C:\TenderAggregator\frontend\src\components\Layout.jsx"

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Добавить tenderMarks в TenderList
old = '<TenderList onSelect={handleSelectTender} selectedId={selectedTender?.id} activeKey={activeKey} />'
new = '<TenderList onSelect={handleSelectTender} selectedId={selectedTender?.id} activeKey={activeKey} tenderMarks={tenderMarks} />'
c = c.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("OK")

