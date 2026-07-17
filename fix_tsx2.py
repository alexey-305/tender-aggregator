path = r'C:\TenderAggregator\frontend\src\components\tenders\TenderList.tsx'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# fix typo: 40b -> 40`
c = c.replace('40b', '40`')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print('OK')