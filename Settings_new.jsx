import { useState, useEffect } from "react";
import api from "../api/client";
import { Plus, Trash2, ArrowLeft, X, ChevronDown } from "lucide-react";
import Modal from "../components/Modal";

const REGIONS_BY_DISTRICT = {
  "ентральный ": ["елгородская обл","рянская обл","ладимирская обл","оронежская обл","вановская обл","алужская обл","остромская обл","урская обл","ипецкая обл","осква","осковская обл","рловская обл","язанская обл","Смоленская обл","Тамбовская обл","Тверская обл","Тульская обл","Ярославская обл"],
  "Северо-ападный ": ["рхангельская обл","ологодская обл","алининградская обл","арелия","оми","енинградская обл","урманская обл","енецкий ","овгородская обл","сковская обл","Санкт-етербург"],
  "жный ": ["дыгея","страханская обл","олгоградская обл","алмыкия","раснодарский край","рым","остовская обл","Севастополь"],
  "Северо-авказский ": ["агестан","нгушетия","абардино-алкария","арачаево-еркесия","Северная сетия","Ставропольский край","ечня"],
  "риволжский ": ["ашкортостан","ировская обл","арий л","ордовия","ижегородская обл","ренбургская обл","ензенская обл","ермский край","Самарская обл","Саратовская обл","Татарстан","дмуртия","льяновская обл","увашия"],
  "ральский ": ["урганская обл","Свердловская обл","Тюменская обл","Ханты-ансийский ","елябинская обл","Ямало-енецкий "],
  "Сибирский ": ["лтай","лтайский край","ркутская обл","емеровская обл","расноярский край","овосибирская обл","мская обл","Томская обл","Тыва","Хакасия"],
  "альневосточный ": ["мурская обл","урятия","врейская ","абайкальский край","амчатский край","агаданская обл","риморский край","Саха (Якутия)","Сахалинская обл","Хабаровский край","укотский "]
};

const PLATFORMS = ["се площадки","ТС-тендер","осэлторг (Т)","Сбербанк-СТ","ZakazRF","Т-Торг","","абрикант","Т ","Bidzaar","B2B-Center","OTC-tender","Тендер.ро","С","Т (ерезка)","азпром","","Сибур","оснефть"];
const METHODS = [{id:"all",label:"се способы"},{id:"electronic_auction",label:"лектронный аукцион"},{id:"request_for_quotations",label:"апрос котировок"},{id:"open_tender",label:"онкурс"},{id:"single_supplier",label:"динственный поставщик"},{id:"request_for_proposals",label:"апрос предложений"},{id:"other",label:"ругие способы"}];
const COLORS = ["#fba500","#d05000","#006b58","#abd848","#962020","#67e2b2","#f4db02","#032fc0","#d681f1"];

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
  const [region, setRegion] = useState("се регионы");
  const [platforms, setPlatforms] = useState(["се площадки"]);
  const [showPlatforms, setShowPlatforms] = useState(false);
  const [methods, setMethods] = useState(["all"]);
  const [showMethods, setShowMethods] = useState(false);
  const [priceFrom, setPriceFrom] = useState("");
  const [priceTo, setPriceTo] = useState("");
  const [notify, setNotify] = useState(false);
  const [lawTypes, setLawTypes] = useState(["44-","223-"]);

  useEffect(() => { api.get("/keys").then(res => setKeys(res.data)).catch(() => {}); api.get("/marks").then(res => setMarks(res.data)).catch(() => {}); }, []);
  const addTag = (value, list, setList) => { if (value.trim() && !list.includes(value.trim())) setList([...list, value.trim()]); };
  const resetForm = () => { setName(""); setKeywords([]); setExcludeWords([]); setRegion("се регионы"); setPriceFrom(""); setPriceTo(""); setNotify(false); setLawTypes(["44-","223-"]); setEditId(null); };
  
  const handleCreate = async () => {
    if (!name.trim()) return;
    if (tab === "keys") {
      const data = { name, keywords: keywords.join(", ") || null, region: region !== "се регионы" ? region : null, price_from: priceFrom || null, price_to: priceTo || null, law: lawTypes.join(", ") };
      if (editId) await api.put("/keys/" + editId, data); else await api.post("/keys", data);
      const r = await api.get("/keys"); setKeys(r.data);
    } else {
      if (editId) await api.put("/marks/" + editId, { name, color }); else await api.post("/marks", { name, color });
      const r = await api.get("/marks"); setMarks(r.data);
    }
    resetForm(); setShowForm(false);
  };
  const handleDelete = async (id) => { if (tab === "keys") { await api.delete("/keys/" + id); setKeys(keys.filter(k => k.id !== id)); } else { await api.delete("/marks/" + id); setMarks(marks.filter(m => m.id !== id)); } };
  const handleEdit = (item) => { setEditId(item.id); setName(item.name); setKeywords(item.keywords ? item.keywords.split(", ") : []); setRegion(item.region || "се регионы"); setShowForm(true); };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] p-8"><div className="max-w-3xl mx-auto">
      <button onClick={() => window.location.href = "/"} className="flex items-center gap-2 text-[var(--text-secondary)] hover:text-white mb-12"><ArrowLeft size={18} /> азад</button>
      <h1 className="text-2xl font-bold text-white mb-10">астройки</h1>
      <div className="flex gap-3 mb-10">
        <button onClick={() => { setTab("keys"); setShowForm(false); }} className={"px-5 py-2.5 rounded-lg text-sm font-medium " + (tab === "keys" ? "bg-[var(--accent)] text-white" : "bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-white")}>Шаблоны</button>
        <button onClick={() => { setTab("marks"); setShowForm(false); }} className={"px-5 py-2.5 rounded-lg text-sm font-medium " + (tab === "marks" ? "bg-[var(--accent)] text-white" : "bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-white")}>етки</button>
      </div>
      {!showForm && <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-5 py-3 rounded-lg bg-[var(--accent)] text-white text-sm font-medium hover:bg-[var(--accent-hover)] mb-10"><Plus size={16} /> Создать {tab === "keys" ? "шаблон" : "метку"}</button>}
      {showForm && tab === "keys" && (
        <div className="bg-[var(--bg-secondary)] p-6 rounded-xl border border-[var(--border)] mb-10 flex flex-col gap-6">
          <h2 className="text-lg font-bold text-white">{editId ? "едактирование" : "овый шаблон"}</h2>
          <input type="text" placeholder="азвание шаблона" value={name} onChange={(e) => setName(e.target.value)} className="w-full p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-white text-sm focus:outline-none focus:border-[var(--accent)]" />
          <div>
            <label className="text-xs text-[var(--text-secondary)] mb-2 block">лючевые слова</label>
            <div className="flex flex-wrap items-center gap-2 p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] min-h-[48px] focus-within:border-[var(--accent)]">
              {keywords.map((kw) => (<span key={kw} className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-[var(--accent)]/20 text-[var(--accent)] text-xs">{kw}<button onClick={() => setKeywords(keywords.filter(k => k !== kw))}><X size={12} /></button></span>))}
              <input type="text" placeholder="Слово + Enter" value={keywordInput} onChange={(e) => setKeywordInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTag(keywordInput, keywords, setKeywords); setKeywordInput(""); } }} className="flex-1 min-w-[120px] bg-transparent border-none outline-none text-sm text-white" />
            </div>
          </div>
          <div>
            <label className="text-xs text-[var(--text-secondary)] mb-2 block">сключать слова</label>
            <div className="flex flex-wrap items-center gap-2 p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] min-h-[48px] focus-within:border-[var(--accent)]">
              {excludeWords.map((kw) => (<span key={kw} className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-red-500/20 text-red-400 text-xs">{kw}<button onClick={() => setExcludeWords(excludeWords.filter(k => k !== kw))}><X size={12} /></button></span>))}
              <input type="text" placeholder="Слово + Enter" value={excludeInput} onChange={(e) => setExcludeInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTag(excludeInput, excludeWords, setExcludeWords); setExcludeInput(""); } }} className="flex-1 min-w-[120px] bg-transparent border-none outline-none text-sm text-white" />
            </div>
          </div>
          <div>
            <label className="text-xs text-[var(--text-secondary)] mb-2 block">егион поставки</label>
            <select value={region} onChange={(e) => setRegion(e.target.value)} className="w-full p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-white text-sm focus:outline-none focus:border-[var(--accent)]">
              <option>се регионы</option>
              {Object.entries(REGIONS_BY_DISTRICT).map(([d, regs]) => (<optgroup key={d} label={d}>{regs.map(r => (<option key={r}>{r}</option>))}</optgroup>))}
            </select>
          </div>
          <div>
            <label className="text-xs text-[var(--text-secondary)] mb-2 block">ачальная цена (RUB)</label>
            <div className="flex items-center gap-2">
              <input type="number" placeholder="т" value={priceFrom} onChange={(e) => setPriceFrom(e.target.value)} className="w-full p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-white text-sm focus:outline-none focus:border-[var(--accent)]" />
              <span className="text-[var(--text-secondary)]">—</span>
              <input type="number" placeholder="о" value={priceTo} onChange={(e) => setPriceTo(e.target.value)} className="w-full p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-white text-sm focus:outline-none focus:border-[var(--accent)]" />
            </div>
          </div>
          <div>
            <label className="text-xs text-[var(--text-secondary)] mb-2 block">Тип торгов</label>
            <div className="flex flex-wrap gap-3">
              {["44-","223-","615 ","оммерческие"].map(t => (
                <label key={t} className="flex items-center gap-1.5 text-sm text-[var(--text-secondary)] cursor-pointer">
                  <input type="checkbox" checked={lawTypes.includes(t)} onChange={() => setLawTypes(prev => prev.includes(t) ? prev.filter(x => x !== t) : [...prev, t])} className="rounded" /> {t}
                </label>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-3 pt-4 border-t border-[var(--border)]">
            <button onClick={handleCreate} className="px-6 py-2.5 rounded-lg bg-[var(--accent)] text-white text-sm font-medium hover:bg-[var(--accent-hover)]">Сохранить и обновить результаты</button>
            <button onClick={() => { setShowForm(false); resetForm(); }} className="px-6 py-2.5 rounded-lg bg-[var(--bg-tertiary)] text-[var(--text-secondary)] text-sm hover:text-white">тменить</button>
            {editId && <button onClick={() => { handleDelete(editId); resetForm(); setShowForm(false); }} className="px-6 py-2.5 rounded-lg bg-red-500/20 text-red-400 text-sm hover:bg-red-500/30 ml-auto">далить</button>}
          </div>
        </div>
      )}
      {showForm && tab === "marks" && (
        <div className="bg-[var(--bg-secondary)] p-6 rounded-xl border border-[var(--border)] mb-10 flex flex-col gap-5">
          <h2 className="text-lg font-bold text-white">{editId ? "едактирование метки" : "овая метка"}</h2>
          <input type="text" placeholder="азвание метки" value={name} onChange={(e) => setName(e.target.value)} className="w-full p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-white text-sm" />
          <div className="flex gap-2 flex-wrap">{COLORS.map((c) => (<button key={c} onClick={() => setColor(c)} className="w-9 h-9 rounded-lg border-2" style={{ backgroundColor: c, borderColor: color === c ? "white" : "transparent" }} />))}</div>
          <div className="flex items-center gap-3 pt-4 border-t border-[var(--border)]">
            <button onClick={handleCreate} className="px-6 py-2.5 rounded-lg bg-[var(--accent)] text-white text-sm font-medium">Сохранить</button>
            <button onClick={() => { setShowForm(false); resetForm(); }} className="px-6 py-2.5 rounded-lg bg-[var(--bg-tertiary)] text-[var(--text-secondary)] text-sm">тменить</button>
            {editId && <button onClick={() => { handleDelete(editId); resetForm(); setShowForm(false); }} className="px-6 py-2.5 rounded-lg bg-red-500/20 text-red-400 text-sm ml-auto">далить</button>}
          </div>
        </div>
      )}
      <div className="flex flex-col gap-3">{(tab === "keys" ? keys : marks).map((item) => (
        <div key={item.id} onClick={() => handleEdit(item)} className="flex items-center justify-between p-4 bg-[var(--bg-secondary)] rounded-xl border border-[var(--border)] hover:border-[var(--accent)]/50 cursor-pointer">
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-3">{tab === "marks" && <div className="w-5 h-5 rounded flex-shrink-0" style={{ backgroundColor: item.color }} />}<span className="text-white font-medium">{item.name}</span></div>
            {tab === "keys" && item.keywords && <div className="flex gap-1 flex-wrap">{item.keywords.split(", ").map((kw) => (<span key={kw} className="px-2 py-0.5 rounded-full bg-[var(--bg-tertiary)] text-[var(--text-secondary)] text-[10px]">{kw}</span>))}</div>}
          </div>
          <button onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }} className="p-2 text-[var(--text-secondary)] hover:text-[var(--danger)] hover:bg-red-500/10 rounded-lg"><Trash2 size={16} /></button>
        </div>
      ))}</div>
    </div></div>
  );
}