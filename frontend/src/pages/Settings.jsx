import { useState, useEffect } from "react";
import api from "../api/client";
import { Plus, Trash2, ArrowLeft, X, ChevronDown } from "lucide-react";
import Modal from "../components/Modal";

const REGIONS = [
  "Все регионы", "Москва", "Московская область", "Санкт-Петербург", "Ленинградская область",
  "Краснодарский край", "Свердловская область", "Татарстан", "Новосибирская область",
  "Ростовская область", "Башкортостан", "Красноярский край", "Челябинская область",
  "Нижегородская область", "Самарская область", "Приморский край", "Саратовская область",
  "Волгоградская область", "Воронежская область", "Пермский край", "Кемеровская область"
];

const PLATFORMS = [
  "Все площадки", "РТС-тендер", "Росэлторг (ЕЭТП)", "Сбербанк-АСТ", "ZakazRF (АГЗРТ)",
  "ТЭК-Торг", "РАД (Lot-Online)", "ЭТП Фабрикант", "ЭТП ГПБ", "Bidzaar", "B2B-Center",
  "OTC-tender", "Тендер.Про", "ЕИС", "Портал поставщиков", "ЕАТ (Березка)", "Газпром", "РЖД", "Сибур", "Роснефть"
];

const METHODS = [
  { id: "all", label: "Все способы" },
  { id: "electronic_auction", label: "Электронный аукцион" },
  { id: "request_for_quotations", label: "Запрос котировок" },
  { id: "open_tender", label: "Конкурс" },
  { id: "single_supplier", label: "Закупка у единственного поставщика" },
  { id: "request_for_proposals", label: "Запрос или мониторинг цен" },
  { id: "other", label: "Другие способы" },
];

const COLORS = ["#fba500", "#d05000", "#006b58", "#abd848", "#962020", "#67e2b2", "#f4db02", "#032fc0", "#d681f1"];

export default function Settings() {
  const [tab, setTab] = useState("keys");
  const [keys, setKeys] = useState([]);
  const [marks, setMarks] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [name, setName] = useState("");
  const [color, setColor] = useState("#fba500");
  const [keywords, setKeywords] = useState([]);
  const [keywordInput, setKeywordInput] = useState("");
  const [excludeWords, setExcludeWords] = useState([]);
  const [excludeInput, setExcludeInput] = useState("");
  const [region, setRegion] = useState("Все регионы");
  const [showRegions, setShowRegions] = useState(false);
  const [platforms, setPlatforms] = useState(["Все площадки"]);
  const [showPlatforms, setShowPlatforms] = useState(false);
  const [methods, setMethods] = useState(["all"]);
  const [showMethods, setShowMethods] = useState(false);
  const [priceFrom, setPriceFrom] = useState("");
  const [priceTo, setPriceTo] = useState("");
  const [notify, setNotify] = useState(false);

  useEffect(() => {
    api.get("/keys").then(res => setKeys(res.data)).catch(() => {});
    api.get("/marks").then(res => setMarks(res.data)).catch(() => {});
  }, []);

  const addTag = (value, list, setList) => {
    if (value.trim() && !list.includes(value.trim())) {
      setList([...list, value.trim()]);
    }
  };

  const toggleItem = (id, list, setList) => {
    if (id === "all") { setList(["all"]); return; }
    let next = list.filter(i => i !== "all");
    if (next.includes(id)) next = next.filter(i => i !== id);
    else next.push(id);
    setList(next.length === 0 ? ["all"] : next);
  };

  const resetForm = () => {
    setName(""); setKeywords([]); setExcludeWords([]); setColor("#fba500");
    setRegion("Все регионы"); setPlatforms(["Все площадки"]); setMethods(["all"]);
    setPriceFrom(""); setPriceTo(""); setNotify(false); setEditId(null);
  };

  const handleCreate = async () => {
    if (!name.trim()) return;
    const data = {
      name, keywords: keywords.join(", ") || null,
      region: region !== "Все регионы" ? region : null,
      price_from: priceFrom || null, price_to: priceTo || null,
    };
    if (editId) {
      await api.put("/keys/" + editId, data);
    } else {
      await api.post("/keys", data);
    }
    resetForm(); setShowForm(false);
    const r = await api.get("/keys"); setKeys(r.data);
  };

  const handleDelete = async (id) => {
    if (tab === "keys") { await api.delete("/keys/" + id); setKeys(keys.filter(k => k.id !== id)); }
    else { await api.delete("/marks/" + id); setMarks(marks.filter(m => m.id !== id)); }
  };

  const handleEdit = (item) => {
    setEditId(item.id); setName(item.name);
    setKeywords(item.keywords ? item.keywords.split(", ") : []);
    setRegion(item.region || "Все регионы");
    setShowForm(true);
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] p-8">
      <div className="max-w-3xl mx-auto">
        <button onClick={() => window.location.href = "/"} className="flex items-center gap-2 text-[var(--text-secondary)] hover:text-white transition-colors mb-12">
          <ArrowLeft size={18} /> Назад
        </button>
        
        <h1 className="text-2xl font-bold text-white mb-10">Настройки</h1>

        <div className="flex gap-3 mb-10">
          <button onClick={() => { setTab("keys"); setShowForm(false); }} className={"px-5 py-2.5 rounded-lg text-sm font-medium transition-colors " + (tab === "keys" ? "bg-[var(--accent)] text-white" : "bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-white")}>Ключи</button>
          <button onClick={() => { setTab("marks"); setShowForm(false); }} className={"px-5 py-2.5 rounded-lg text-sm font-medium transition-colors " + (tab === "marks" ? "bg-[var(--accent)] text-white" : "bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-white")}>Метки</button>
        </div>

        {!showForm && (
          <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-5 py-3 rounded-lg bg-[var(--accent)] text-white text-sm font-medium hover:bg-[var(--accent-hover)] transition-colors mb-10">
            <Plus size={16} /> Создать {tab === "keys" ? "ключ" : "метку"}
          </button>
        )}

        {showForm && tab === "keys" && (
          <div className="bg-[var(--bg-secondary)] p-6 rounded-xl border border-[var(--border)] mb-10 flex flex-col gap-6">
            <h2 className="text-lg font-bold text-white">{editId ? "Редактирование ключа" : "Новый ключ"}</h2>

            <input type="text" placeholder="Название ключа" value={name} onChange={(e) => setName(e.target.value)}
              className="w-full p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-white text-sm focus:outline-none focus:border-[var(--accent)]" />

            <label className="flex items-center gap-2 text-sm text-[var(--text-secondary)] cursor-pointer">
              <input type="checkbox" checked={notify} onChange={(e) => setNotify(e.target.checked)} className="rounded" />
              Уведомления на почту о новых закупках (раз в сутки)
            </label>

            <div>
              <label className="text-xs text-[var(--text-secondary)] mb-2 block">Ключевые слова</label>
              <div className="flex flex-wrap items-center gap-2 p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] min-h-[48px] focus-within:border-[var(--accent)]">
                {keywords.map((kw) => (
                  <span key={kw} className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-[var(--accent)]/20 text-[var(--accent)] text-xs">
                    {kw}<button onClick={() => setKeywords(keywords.filter(k => k !== kw))}><X size={12} /></button>
                  </span>
                ))}
                <input type="text" placeholder="Слово + Enter" value={keywordInput} onChange={(e) => setKeywordInput(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTag(keywordInput, keywords, setKeywords); setKeywordInput(""); } }}
                  className="flex-1 min-w-[120px] bg-transparent border-none outline-none text-sm text-white placeholder-[var(--text-secondary)]" />
              </div>
            </div>

            <div>
              <label className="text-xs text-[var(--text-secondary)] mb-2 block">Исключать слова</label>
              <div className="flex flex-wrap items-center gap-2 p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] min-h-[48px] focus-within:border-[var(--accent)]">
                {excludeWords.map((kw) => (
                  <span key={kw} className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-red-500/20 text-red-400 text-xs">
                    {kw}<button onClick={() => setExcludeWords(excludeWords.filter(k => k !== kw))}><X size={12} /></button>
                  </span>
                ))}
                <input type="text" placeholder="Слово + Enter" value={excludeInput} onChange={(e) => setExcludeInput(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTag(excludeInput, excludeWords, setExcludeWords); setExcludeInput(""); } }}
                  className="flex-1 min-w-[120px] bg-transparent border-none outline-none text-sm text-white placeholder-[var(--text-secondary)]" />
              </div>
            </div>

            <div>
              <label className="text-xs text-[var(--text-secondary)] mb-2 block">Регион поставки</label>
              <button onClick={() => setShowRegions(true)} className="flex items-center justify-between w-full p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-white text-sm hover:border-[var(--accent)] transition-colors">
                {region} <ChevronDown size={16} />
              </button>
            </div>

            <div>
              <label className="text-xs text-[var(--text-secondary)] mb-2 block">Тип торгов</label>
              <div className="flex flex-wrap gap-2">
                {["44-ФЗ", "223-ФЗ", "615 ПП", "Коммерческие"].map(t => (
                  <label key={t} className="flex items-center gap-1.5 text-sm text-[var(--text-secondary)] cursor-pointer">
                    <input type="checkbox" className="rounded" /> {t}
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs text-[var(--text-secondary)] mb-2 block">Способ отбора</label>
              <button onClick={() => setShowMethods(true)} className="flex items-center justify-between w-full p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-white text-sm hover:border-[var(--accent)]">
                {methods.includes("all") ? "Все способы" : methods.map(m => METHODS.find(x => x.id === m)?.label).join(", ")} <ChevronDown size={16} />
              </button>
            </div>

            <div>
              <label className="text-xs text-[var(--text-secondary)] mb-2 block">Площадка</label>
              <button onClick={() => setShowPlatforms(true)} className="flex items-center justify-between w-full p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-white text-sm hover:border-[var(--accent)]">
                {platforms.includes("Все площадки") ? "Все площадки" : platforms.join(", ")} <ChevronDown size={16} />
              </button>
            </div>

            <div>
              <label className="text-xs text-[var(--text-secondary)] mb-2 block">Начальная цена (RUB)</label>
              <div className="flex items-center gap-2">
                <input type="number" placeholder="От" value={priceFrom} onChange={(e) => setPriceFrom(e.target.value)}
                  className="w-full p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-white text-sm focus:outline-none focus:border-[var(--accent)]" />
                <span className="text-[var(--text-secondary)]">—</span>
                <input type="number" placeholder="До" value={priceTo} onChange={(e) => setPriceTo(e.target.value)}
                  className="w-full p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-white text-sm focus:outline-none focus:border-[var(--accent)]" />
              </div>
            </div>

            <div className="flex items-center gap-3 pt-4 border-t border-[var(--border)]">
              <button onClick={handleCreate} className="px-6 py-2.5 rounded-lg bg-[var(--accent)] text-white text-sm font-medium hover:bg-[var(--accent-hover)] transition-colors">
                Сохранить и обновить результаты
              </button>
              <button onClick={() => { setShowForm(false); resetForm(); }} className="px-6 py-2.5 rounded-lg bg-[var(--bg-tertiary)] text-[var(--text-secondary)] text-sm hover:text-white transition-colors">
                Отменить
              </button>
              {editId && (
                <button onClick={() => { handleDelete(editId); resetForm(); setShowForm(false); }} className="px-6 py-2.5 rounded-lg bg-red-500/20 text-red-400 text-sm hover:bg-red-500/30 transition-colors ml-auto">
                  Удалить шаблон
                </button>
              )}
            </div>
          </div>
        )}

        {showForm && tab === "marks" && (
          <div className="bg-[var(--bg-secondary)] p-6 rounded-xl border border-[var(--border)] mb-10 flex flex-col gap-5">
            <h2 className="text-lg font-bold text-white">{editId ? "Редактирование метки" : "Новая метка"}</h2>
            <input type="text" placeholder="Название метки" value={name} onChange={(e) => setName(e.target.value)}
              className="w-full p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-white text-sm focus:outline-none focus:border-[var(--accent)]" />
            <div className="flex gap-2 flex-wrap">
              {COLORS.map((c) => (
                <button key={c} onClick={() => setColor(c)} className="w-9 h-9 rounded-lg border-2 transition-all hover:scale-110" style={{ backgroundColor: c, borderColor: color === c ? "white" : "transparent" }} />
              ))}
            </div>
            <div className="flex items-center gap-3 pt-4 border-t border-[var(--border)]">
              <button onClick={handleCreate} className="px-6 py-2.5 rounded-lg bg-[var(--accent)] text-white text-sm font-medium hover:bg-[var(--accent-hover)]">Сохранить</button>
              <button onClick={() => { setShowForm(false); resetForm(); }} className="px-6 py-2.5 rounded-lg bg-[var(--bg-tertiary)] text-[var(--text-secondary)] text-sm hover:text-white">Отменить</button>
              {editId && (
                <button onClick={() => { handleDelete(editId); resetForm(); setShowForm(false); }} className="px-6 py-2.5 rounded-lg bg-red-500/20 text-red-400 text-sm hover:bg-red-500/30 ml-auto">Удалить</button>
              )}
            </div>
          </div>
        )}

        <div className="flex flex-col gap-3">
          {(tab === "keys" ? keys : marks).map((item) => (
            <div key={item.id} onClick={() => handleEdit(item)} className="flex items-center justify-between p-4 bg-[var(--bg-secondary)] rounded-xl border border-[var(--border)] hover:border-[var(--accent)]/50 transition-colors cursor-pointer">
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-3">
                  {tab === "marks" && <div className="w-5 h-5 rounded flex-shrink-0" style={{ backgroundColor: item.color }} />}
                  <span className="text-white font-medium">{item.name}</span>
                </div>
                {tab === "keys" && item.keywords && (
                  <div className="flex gap-1 flex-wrap">
                    {item.keywords.split(", ").map((kw) => (
                      <span key={kw} className="px-2 py-0.5 rounded-full bg-[var(--bg-tertiary)] text-[var(--text-secondary)] text-[10px]">{kw}</span>
                    ))}
                  </div>
                )}
              </div>
              <button onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }} className="p-2 text-[var(--text-secondary)] hover:text-[var(--danger)] hover:bg-red-500/10 rounded-lg transition-colors">
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      </div>

      <Modal isOpen={showRegions} onClose={() => setShowRegions(false)} title="Регион поставки"
        footer={<>
          <button onClick={() => setShowRegions(false)} className="px-5 py-2 rounded-lg bg-[var(--accent)] text-white text-sm font-medium hover:bg-[var(--accent-hover)]">Выбрать</button>
          <button onClick={() => setShowRegions(false)} className="px-5 py-2 rounded-lg bg-[var(--bg-tertiary)] text-[var(--text-secondary)] text-sm hover:text-white">Отменить</button>
        </>}>
        <div className="flex flex-col gap-1 max-h-96 overflow-y-auto">
          {REGIONS.map((r) => (
            <button key={r} onClick={() => setRegion(r)}
              className={"text-left px-3 py-2 rounded-lg text-sm transition-colors " + (region === r ? "bg-[var(--accent)]/20 text-[var(--accent)]" : "text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] hover:text-white")}>
              {r}
            </button>
          ))}
        </div>
      </Modal>

      <Modal isOpen={showPlatforms} onClose={() => setShowPlatforms(false)} title="Площадки"
        footer={<>
          <button onClick={() => setShowPlatforms(false)} className="px-5 py-2 rounded-lg bg-[var(--accent)] text-white text-sm font-medium hover:bg-[var(--accent-hover)]">Применить</button>
          <button onClick={() => setShowPlatforms(false)} className="px-5 py-2 rounded-lg bg-[var(--bg-tertiary)] text-[var(--text-secondary)] text-sm hover:text-white">Отменить</button>
        </>}>
        <div className="flex flex-col gap-1 max-h-96 overflow-y-auto">
          {PLATFORMS.map((p) => (
            <label key={p} className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] cursor-pointer">
              <input type="checkbox" checked={platforms.includes(p)} onChange={() => toggleItem(p, platforms, setPlatforms)} className="rounded" />
              {p}
            </label>
          ))}
        </div>
      </Modal>

      <Modal isOpen={showMethods} onClose={() => setShowMethods(false)} title="Способ отбора"
        footer={<>
          <button onClick={() => setShowMethods(false)} className="px-5 py-2 rounded-lg bg-[var(--accent)] text-white text-sm font-medium hover:bg-[var(--accent-hover)]">Применить</button>
          <button onClick={() => setShowMethods(false)} className="px-5 py-2 rounded-lg bg-[var(--bg-tertiary)] text-[var(--text-secondary)] text-sm hover:text-white">Отменить</button>
        </>}>
        <div className="flex flex-col gap-1">
          {METHODS.map((m) => (
            <label key={m.id} className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] cursor-pointer">
              <input type="checkbox" checked={methods.includes(m.id)} onChange={() => toggleItem(m.id, methods, setMethods)} className="rounded" />
              {m.label}
            </label>
          ))}
        </div>
      </Modal>
    </div>
  );
}