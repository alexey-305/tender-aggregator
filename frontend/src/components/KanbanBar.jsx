import { useState, useEffect, useRef } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

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

  const getColumnTenders = (colId) => {
    const col = COLUMNS.find(c => c.id === colId);
    if (!col) return [];
    if (colId === "new") {
      return tenders.filter(t => !tenderMarks[t.id] || tenderMarks[t.id].length === 0);
    }
    return tenders.filter(t => {
      const marks = tenderMarks[t.id] || [];
      return marks.some(m => col.markNames.includes(m.name || m));
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
      return marks.some(m => col.markNames.includes(m.name || m));
    }).length;
  };

  return (
    <div className="border-b border-[var(--border)]" ref={panelRef}>
      {/* Верхняя строка с кнопками колонок */}
      <div className="flex items-center px-4 py-2 gap-2">
        {COLUMNS.map((col) => (
          <button
            key={col.id}
            onClick={() => setExpanded(expanded === col.id ? null : col.id)}
            className={"flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex-1 justify-center " + (expanded === col.id ? "bg-[var(--bg-tertiary)] text-white" : "bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] hover:text-white")}
          >
            <div className={"w-2 h-2 rounded-full " + col.color} />
            {col.title}
            <span className="text-[var(--text-secondary)]">{getColumnCount(col.id)}</span>
            {expanded === col.id ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>
        ))}
      </div>

      {/* Раскрывашка с плашками */}
      {expanded && (
        <div className="max-h-56 overflow-y-auto border-t border-[var(--border)] bg-[var(--bg-secondary)]">
          {(() => {
            const colTenders = getColumnTenders(expanded);
            if (colTenders.length === 0) {
              return <div className="text-xs text-[var(--text-secondary)] text-center py-6">Нет закупок в этой колонке</div>;
            }
            return (
              <div className="p-3 grid grid-cols-2 lg:grid-cols-3 gap-2">
                {colTenders.map((tender) => {
                  const price = tender.initial_price ? Number(tender.initial_price).toLocaleString("ru-RU") : "";
                  const deadline = tender.submission_deadline ? new Date(tender.submission_deadline).toLocaleDateString("ru-RU") : "";
                  return (
                    <div
                      key={tender.id}
                      onClick={() => { onSelectTender && onSelectTender(tender); setExpanded(null); }}
                      className="bg-[var(--bg-tertiary)] p-2.5 rounded-lg border border-[var(--border)] cursor-pointer hover:border-[var(--accent)]/50 transition-colors flex items-center justify-between gap-3"
                    >
                      <div className="flex-1 min-w-0">
                        <h4 className="text-xs font-medium text-white truncate">{tender.title}</h4>
                        <p className="text-[10px] text-[var(--text-secondary)] truncate mt-0.5">{tender.customer?.name || tender.customer || ""}</p>
                      </div>
                      <div className="text-right flex-1 justify-center">
                        {price && <div className="text-xs font-semibold text-white">{price} ₽</div>}
                        {deadline && <div className="text-[10px] text-[var(--text-secondary)]">{deadline}</div>}
                      </div>
                    </div>
                  );
                })}
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
}