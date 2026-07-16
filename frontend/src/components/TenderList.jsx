import { useState, useEffect } from "react";
import api from "../api/client";
import { Search, Plus, ChevronDown } from "lucide-react";

const METHOD_ABBR = {
  electronic_auction: "ЭА",
  open_tender: "ОК",
  request_for_quotations: "ЗК",
  request_for_proposals: "ЗП",
  single_supplier: "ЕП",
  two_stage_tender: "ДК",
  open_tender_limited: "КОУ",
  commercial_other: "К",
};

function getDaysLeft(dateStr) {
  if (!dateStr) return null;
  return Math.ceil((new Date(dateStr) - new Date()) / (1000 * 60 * 60 * 24));
}

function getStage(tender) {
  const now = new Date();
  const deadline = tender.submission_deadline ? new Date(tender.submission_deadline) : null;
  const summarizing = tender.summarizing_date ? new Date(tender.summarizing_date) : null;
  
  if (!deadline) return tender.published_at ? "Опубликовано" : "—";
  
  const days = getDaysLeft(tender.submission_deadline);
  if (days === null) return "—";
  if (days < 0) {
    if (summarizing && now < summarizing) return "Работа комиссии";
    if (summarizing && now >= summarizing) return "Завершено";
    return "Завершено";
  }
  if (days <= 3) return "Срочно";
  return "Подача заявок";
}

function getStageColor(tender) {
  const days = getDaysLeft(tender.submission_deadline);
  if (days === null) return "text-[var(--text-secondary)]";
  if (days < 0) return "text-[var(--text-secondary)]";
  if (days <= 3) return "text-[var(--danger)]";
  return "text-green-400";
}

function getDeadlineColor(dateStr) {
  if (!dateStr) return "text-[var(--text-secondary)]";
  const days = getDaysLeft(dateStr);
  if (days === null) return "text-[var(--text-secondary)]";
  if (days < 0) return "text-[var(--text-secondary)]";
  if (days <= 3) return "text-[var(--danger)]";
  if (days <= 7) return "text-[var(--warning)]";
  return "text-white";
}

function formatDate(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("ru-RU");
}

function groupByDate(tenders) {
  const groups = {};
  tenders.forEach((t) => {
    const d = t.published_at ? new Date(t.published_at).toLocaleDateString("ru-RU") : "Без даты";
    if (!groups[d]) groups[d] = [];
    groups[d].push(t);
  });
  return Object.entries(groups).sort((a, b) => new Date(b[0].split(".").reverse().join("-")) - new Date(a[0].split(".").reverse().join("-")));
}

export default function TenderList({ onSelect, selectedId, activeKey }) {
  const [tenders, setTenders] = useState([]);
  const [searchNumber, setSearchNumber] = useState("");

  useEffect(() => { console.log("activeKey:", activeKey);
    api.get(activeKey ? "/tenders/filter?keywords=" + encodeURIComponent(activeKey.keywords || "") + "&region=" + (activeKey.region || "") + "&law=" + (activeKey.law || "") + "&price_from=" + (activeKey.price_from || "") + "&price_to=" + (activeKey.price_to || "") + "&platforms=" + (activeKey.platforms || "") + "&methods=" + (activeKey.methods || "") : "/tenders?limit=100").then((res) => { setTenders(res.data); }).catch(() => {});
  }, [activeKey]);

  const grouped = groupByDate(tenders);

  return (
    <div className="h-full flex flex-col bg-[var(--bg-primary)]">
      <div className="p-3 border-b border-[var(--border)]">
        <div className="relative mb-2">
          <input type="text" placeholder="Поиск извещений..." value={searchNumber} onChange={(e) => setSearchNumber(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-sm text-white focus:outline-none focus:border-[var(--accent)]" />
          <Search size={15} className="absolute left-3 top-2.5 text-[var(--text-secondary)]" />
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
            <button className="flex items-center gap-1 hover:text-white"><span className="font-medium">Дата окончания</span><ChevronDown size={12} /></button>
            <button className="hover:text-white">Цена</button>
            <button className="hover:text-white">Ещё</button>
          </div>
          <button className="w-7 h-7 rounded-lg bg-[var(--accent)]/20 text-[var(--accent)] flex items-center justify-center hover:bg-[var(--accent)]/30"><Plus size={16} /></button>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto">
        {grouped.map(([date, items]) => (
          <div key={date}>
            <div className="px-3 py-1.5 text-xs text-[var(--text-secondary)] bg-[var(--bg-secondary)] border-b border-[var(--border)] font-medium sticky top-0 z-10">{date}</div>
            {items.map((tender) => {
              const price = tender.initial_price ? Number(tender.initial_price).toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "";
              const stage = getStage(tender);
              const stageColor = getStageColor(tender);
              return (
                <div key={tender.id} onClick={() => onSelect(tender)}
                  className={"flex border-b border-[var(--border)] cursor-pointer hover:bg-[var(--bg-tertiary)] transition-colors " + (selectedId === tender.id ? "bg-[var(--bg-tertiary)]" : "")}>
                  <div className="w-1 flex-shrink-0 bg-[var(--accent)]" style={{ opacity: selectedId === tender.id ? 1 : 0 }} />
                  <div className="flex-1 min-w-0 p-3">
                    <h3 className="text-sm font-medium leading-snug text-white line-clamp-2 mb-1.5">{tender.title}</h3>
                    <div className="flex items-center gap-3 text-xs">
                      <span className="px-1.5 py-0.5 rounded text-[11px] font-semibold bg-blue-500/20 text-blue-400 flex-shrink-0">{METHOD_ABBR[tender.procurement_method] || "—"}</span>
                      <span className={getDeadlineColor(tender.submission_deadline) + " flex-shrink-0"}>
                        {tender.submission_deadline ? "до " + formatDate(tender.submission_deadline) : formatDate(tender.published_at)}
                      </span>
                      <span className={stageColor + " flex-shrink-0"}>{stage}</span>
                      {price && <span className="font-semibold text-white truncate">{price} RUB</span>}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}


