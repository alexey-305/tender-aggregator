import { Star, Calendar, Building2 } from "lucide-react";

export default function TenderList({ onSelect, selectedId, activeKey, tenderMarks = {}, tenders = [] }) {

  const getStatusColor = (tender) => {
    const marks = tenderMarks[tender.id] || [];
    if (marks.length > 0 && typeof marks[0] === 'object' && marks[0].color) return marks[0].color;
    if (marks.length > 0 && typeof marks[0] === 'string') return "#ff6b6b";
    const now = new Date();
    const deadline = new Date(tender.deadline || tender.submission_deadline);
    if (deadline && !isNaN(deadline)) {
      const hoursLeft = (deadline.getTime() - now.getTime()) / (1000 * 60 * 60);
      if (hoursLeft <= 24 && hoursLeft > 0) return "#ef4444";
    }
    if (tender.isFavorite) return "#3b82f6";
    return "transparent";
  };

  const getStatusLabel = (status) => {
    if (!status || status === 'unknown') return 'Активен';
    const labels = { 'submission_open': 'Подача', 'submission_closed': 'Закрыт', 'winner_determined': 'Определён', 'cancelled': 'Отменён' };
    return labels[status] || status;
  };

  const grouped = {};
  tenders.forEach(tender => {
    const d = tender.published_at ? new Date(tender.published_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }) : 'Без даты';
    if (!grouped[d]) grouped[d] = [];
    grouped[d].push(tender);
  });
  const today = new Date().toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
  const yesterday = new Date(Date.now() - 86400000).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
  const getGroupLabel = (d) => d === today ? 'Сегодня' : d === yesterday ? 'Вчера' : d;

  return (
    <div className="h-full overflow-y-auto bg-[var(--bg-primary)]">
      <div className="p-3">
        <div className="flex justify-between items-center mb-3">
          <h1 className="text-lg font-bold text-white">Закупки</h1>
          <div className="text-xs text-[var(--text-secondary)]">Найдено: <span className="font-semibold text-white">{tenders.length}</span></div>
        </div>
        {Object.entries(grouped).map(([date, dayTenders]) => (
          <div key={date} className="mb-4">
            <div className="flex items-center gap-3 mb-2 px-1">
              <div className="h-px flex-1 bg-[var(--border)]"></div>
              <span className="text-xs font-medium text-[var(--text-secondary)] whitespace-nowrap">{getGroupLabel(date)} </span>
              <div className="h-px flex-1 bg-[var(--border)]"></div>
            </div>
            <div className="space-y-2">
              {dayTenders.map((tender) => (
                <div key={tender.id} onClick={() => onSelect && onSelect(tender)} className={`border hover:shadow-md transition-all duration-200 flex overflow-hidden cursor-pointer ${selectedId === tender.id ? 'border-blue-400 shadow-md bg-[var(--bg-secondary)]' : 'border-[var(--border)] bg-[var(--bg-secondary)]'}`}>
                  <div className="w-1.5 flex-shrink-0" style={{ background: getStatusColor(tender) === 'transparent' ? 'transparent' : `linear-gradient(180deg, ${getStatusColor(tender)} 0%, ${getStatusColor(tender)}cc 100%)`, boxShadow: getStatusColor(tender) === 'transparent' ? 'none' : `0 0 8px ${getStatusColor(tender)}80` }} />
                  <div className="flex-1 p-3 min-w-0">
                    <div className="flex items-start gap-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-white leading-snug truncate">{tender.title}</h3>
                        <p className="text-xs text-[var(--text-secondary)] mt-0.5 flex items-center gap-1"><Building2 className="h-3 w-3 flex-shrink-0" /><span className="truncate">{tender.customer?.name || tender.customer || "—"}</span></p>
                      </div>
                      <button className="text-yellow-500 hover:text-yellow-600 flex-shrink-0 mt-0.5"><Star className={tender.isFavorite ? "fill-current" : ""} size={16} /></button>
                    </div>
                    <div className="grid grid-cols-3 gap-2 mt-2 text-xs">
                      <div><p className="text-[var(--text-secondary)]">Цена</p><p className="font-semibold text-white">{tender.initial_price ? Number(tender.initial_price).toLocaleString('ru-RU') + ' ₽' : tender.price ? Number(tender.price).toLocaleString('ru-RU') + ' ₽' : '—'}</p></div>
                      <div><p className="text-[var(--text-secondary)]">Дедлайн</p><p className="font-medium text-[var(--text-secondary)] flex items-center gap-0.5"><Calendar className="h-3 w-3" />{tender.submission_deadline ? new Date(tender.submission_deadline).toLocaleDateString('ru-RU') : tender.deadline || '—'}</p></div>
                      <div><p className="text-[var(--text-secondary)]">Статус</p><span className="inline-block px-2 py-0.5 bg-green-500/20 text-green-400 rounded-full text-xs font-medium">{getStatusLabel(tender.status)}</span></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}