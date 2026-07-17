path = r'C:\TenderAggregator\frontend\src\components\tenders\TenderList.tsx'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Добавить четыре поля в props
line1 = 'export default function TenderList() {'
line2 = 'export default function TenderList({ onSelect, selectedId, activeKey, tenderMarks = {} }) {'
c = c.replace(line1, line2)

# 2. Добавить разбор цвета и з tenderMarks
if 'tenderMarks' in c:
    # Уже есть, обработываем getStatusColor должен использовать цвет из меток без триммерного статуса
    c = c.replace(
        'const getStatusColor = (tender: any) => {',
        'const getStatusColor = (tender: any) => {\n    const marks = tenderMarks[tender.id] || [];\n    if (marks.length > 0) {\n      return '#ff6b6b'; // цвет метки из TenderCard\n    }\n    '
    )

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print('OK')