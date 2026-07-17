path = r'C:\TenderAggregator\frontend\src\components\tenders\TenderList.tsx'

content = """import { useState } from \"react\";
import { Star, Calendar, Building2 } from \"lucide-react\";

export default function TenderList({ onSelect, selectedId, activeKey, tenderMarks = {} }) {
  const [tenders] = useState([
    {
      id: \"0348300000126000123\",
      title: \"Поставка металлоконструкций для строительства\",
      customer: \"МКУ 'Городское хозяйство'\",
      region: \"Москва\",
      price: \"12450000\",
      deadline: \"2026-07-20\",
      status: \"Подача заявок\",
      law: \"44-ФЗ\",
      isFavorite: true,
    },
    {
      id: \"223-ФЗ-456789\",
      title: \"Оказание услуг по уборке территории\",
      customer: \"ООО Ромашка\",
      region: \"Московская область\",
      price: \"2450000\",
      deadline: \"2026-07-15\",
      status: \"Подача заявок\",
      law: \"223-ФЗ\",
      isFavorite: false,
    }
  ]);

  const getStatusColor = (tender: any) => {
    const marks = tenderMarks[tender.id] || [];
    if (marks.length > 0) return \"#ff6b6b\";
    const now = new Date();
    const deadline = new Date(tender.deadline);
    const hoursLeft = (deadline.getTime() - now.getTime()) / (1000 * 60 * 60);
    if (hoursLeft <= 24 && hoursLeft > 0) return \"#ef4444\";
    if (tender.isFavorite) return \"#3b82f6\";
    if (hoursLeft <= 0) return \"#9ca3af\";
    return \"#eab308\";
  };

  return (
    <div className=\"space-y-4\">
      <div className=\"flex justify-between items-center mb-6\">
        <h1 className=\"text-3xl font-bold text-gray-900\">Закупки</h1>
        <div className=\"text-sm text-gray-500\">
          Найдено: <span className=\"font-semibold text-gray-900\">1 247</span>
        </div>
      </div>

      <div className=\"grid gap-4\">
        {tenders.map((tender) => (
          <div key={tender.id} className=\"bg-white border border-gray-200 rounded-2xl hover:shadow-lg transition-all duration-200 flex overflow-hidden\">
            <div className=\"w-1.5 flex-shrink-0 rounded-l-2xl\" style={{ background: `linear-gradient(180deg, ${getStatusColor(tender)}80 0%, ${getStatusColor(tender)} 100%)`, boxShadow: `0 0 8px ${getStatusColor(tender)}40` }} />
            <div className=\"flex-1 p-6\">
              <div className=\"flex justify-between items-start\">
                <div className=\"flex-1\">
                  <div className=\"flex items-center gap-3\">
                    <span className=\"inline-block px-3 py-1 text-xs font-medium bg-blue-100 text-blue-700rounded-full\">
                      {tender.law}
                    </span>
                    <h3 className=\"font-semibold text-lg leading-tight\">{tender.title}</h3>
                  </div>
                  <p className=\"text-gray-600 mt-2 flex items-center gap-2\">
                    <Building2 className=\"h-4 w-4\" />
                    {tender.customer} • {tender.region}
                  </p>
                </div>

                <button className=\"text-yellow-500 hover:text-yellow-600\">
                  <Star className={tender.isFavorite ? \"fill-current\" : \"\"} size={24} />
                </button>
              </div>

              <div className=\"grid grid-cols-3 gap-6 mt-6 text-sm\">
                <div>
                  <p className=\"text-gray-500\">Цена</p>
                  <p className=\"font-semibold text-lg\">{Number(tender.price).toLocaleString('ru-RU')} ₭</p>
                </div>
                <div>
                  <p className=\"text-gray-500\">Дедлайн</p>
                  <p className=\"font-medium flex items-center gap-1\">
                    <Calendar className=\"h-4 w-4\" /> {tender.deadline}
                  </p>
                </div>
                <div>
                  <p className=\"text-gray-500\">Статус</p>
                  <span className=\"inline-block px-4 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium\">
                    {tender.status}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('OK')