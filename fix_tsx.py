path = r'C:\TenderAggregator\frontend\src\components\tenders\TenderList.tsx'

found = False
for enc in ['utf-8', 'windows-1251', 'utf-16', 'cp1251', 'latin-1']:
    try:
        with open(path, 'r', encoding=enc) as f:
            c = f.read()
            found = True
            print(f"Encoding: {enc}")
            break
    except:
        pass

if not found:
    print("NOT FOUND")
    exit(1)

c = c.replace(
    '  return (',
    '''  const getStatusColor = (tender: any) => {
    const now = new Date();
    const deadline = new Date(tender.deadline);
    const hoursLeft = (deadline.getTime() - now.getTime()) / (1000 * 60 * 60);
    if (hoursLeft <= 24 && hoursLeft > 0) return "#ef4444";
    if (tender.isFavorite) return "#3b82f6";
    if (hoursLeft <= 0) return "#9ca3af";
    return "#eab308";
  };

  return ('''
)

c = c.replace(
    '<div key={tender.id} className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-lg transition-all duration-200">\n            <div className="flex justify-between items-start">',
    '<div key={tender.id} className="bg-white border border-gray-200 rounded-2xl hover:shadow-lg transition-all duration-200 flex overflow-hidden">\n              <div className="w-1.5 flex-shrink-0 rounded-l-2xl" style={{ background: `linear-gradient(180deg, ${getStatusColor(tender)}80 0%, ${getStatusColor(tender)} 100%)`, boxShadow: `0 0 8px ${getStatusColor(tender)}40b }} />\n              <div className="flex-1 p-6">\n                <div className="flex justify-between items-start">'
)

c = c.replace(
    '</div>\n            </div>\n          </div>\n        ))}',
    '</div>\n            </div>\n          </div>\n          </div>\n        ))}'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print('OK')