import { useState, useEffect, useRef } from "react";
import { ChevronDown, ChevronUp, GripVertical } from "lucide-react";

const COLUMNS = [
  { id: "new", title: "Новые", color: "bg-blue-500", markNames: [] },
  { id: "analysis", title: "Согласование", color: "bg-yellow-500", markNames: ["Согласование"] },
  { id: "preparation", title: "Участвуем", color: "bg-purple-500", markNames: ["Участвуем"] },
  { id: "submitted", title: "Подано", color: "bg-green-500", markNames: ["Подана заявка"] },
  { id: "won", title: "Победа", color: "bg-emerald-400", markNames: ["Победа"] },
  { id: "contract", title: "Подписание", color: "bg-amber-400", markNames: ["Подписание контракта"] },
  { id: "execution", title: "Исполнение", color: "bg-indigo-500", markNames: ["Исполнение"] },
  { id: "lost", title: "Отказ", color: "bg-red-500", markNames: ["Отказ от участия"] },
];

export default function KanbanBar({ tenders, onSelectTender, tenderMarks }) {
  const [expanded, setExpanded] = useState(null);
  const panelRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setExpanded(null);
      }
    };
    if (expanded) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [expanded]);

  // Подсчёт закупок в каждой колонке на основе меток
  const getColumnTenders = (colId) => {
    const col = COLUMNS.find(c => c.id === colId);
    if (!col) return [];
    
    if (colId === "new") {
      // В "Новые" попадают закупки без меток
      return tenders.filter(t => !tenderMarks[t.id] || tenderMarks[t.id].length === 0);
    }
    
    return tenders.filter(t => {
      const marks = tenderMarks[t.id] || [];
      return marks.some(m => col.markNames.includes(m));
    });
  };

  const getColumnCount = (colId) => {
    const col = COLUMNS.find(c => c.id === colId);
    if (!col) return 0;
    if (colId === "new") {
      return tenders.filter(t => !tenderMarks[t.id] || tenderMarks[t.id].length === 0).length;
    }
    return tenders.filter(t => {
      const marks = tenderMarks[t.id] || [];
      return marks.some(m => col.markNames.includes(m));
    }).length;
  };

  const filteredTenders = expanded ? getColumnTenders(expanded) : [];

  return (
    <div className="border-b border-[var(--border)]" ref={panelRef}>
      <div className="flex items-center px-4 py-2 gap-1 overflow-x-auto">
        {COLUMNS.map((col) => (
          <button
            key={col.id}
            onClick={() => setExpanded(expanded === col.id ? null : col.id)}
            className={"flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex-shrink-0 " + (expanded === col.id ? "bg-[var(--bg-tertiary)] text-white" : "bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] hover:text-white")}
          >
            <div className={"w-2 h-2 rounded-full " + col.color} />
            {col.title}
            <span className="text-[var(--text-secondary)]">{getColumnCount(col.id)}</span>
            {expanded === col.id ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>
        ))}
      </div>

      {expanded && (
        <div className="max-h-64 overflow-y-auto border-t border-[var(--border)] bg-[var(--bg-secondary)]">
          {filteredTenders.length === 0 ? (
            <div className="text-xs text-[var(--text-secondary)] text-center py-8">Нет закупок в этой колонке</div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2 p-3">
              {filteredTenders.map((tender) => {
                const price = tender.initial_price ? Number(tender.initial_price).toLocaleString("ru-RU") : "";
                const marks = tenderMarks[tender.id] || [];
                return (
                  <div
                    key={tender.id}
                    onClick={() => { onSelectTender && onSelectTender(tender); setExpanded(null); }}
                    className="bg-[var(--bg-tertiary)] p-3 rounded-xl border border-[var(--border)] cursor-pointer hover:border-[var(--accent)]/50 transition-colors"
                  >
                    <h4 className="text-xs font-medium text-white line-clamp-2 mb-1">{tender.title}</h4>
                    {marks.length > 0 && (
                      <div className="flex gap-1 mb-1 flex-wrap">
                        {marks.map((m, i) => (
                          <span key={i} className="px-1.5 py-0.5 rounded text-[9px] bg-[var(--bg-secondary)] text-[var(--text-secondary)]">{m}</span>
                        ))}
                      </div>
                    )}
                    {price && <span className="text-[10px] font-semibold text-white">{price} RUB</span>}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}