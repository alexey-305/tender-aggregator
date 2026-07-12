import { useState, useEffect } from "react";
import api from "../api/client";
import { Plus, Trash2, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Settings() {
  const [keys, setKeys] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/keys").then((res) => setKeys(res.data)).catch(() => {});
  }, []);

  const handleCreate = async () => {
    if (!name.trim()) return;
    await api.post("/keys", { name });
    setName("");
    setShowForm(false);
    const res = await api.get("/keys");
    setKeys(res.data);
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] p-8">
      <div className="max-w-2xl mx-auto">
        <button onClick={() => window.location.href = "/"} className="flex items-center gap-2 text-[var(--text-secondary)] hover:text-white mb-6">
          <ArrowLeft size={18} /> Назад
        </button>
        <h1 className="text-2xl font-bold text-white mb-6">Настройки ключей</h1>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-[var(--accent)] text-white text-sm font-medium hover:bg-[var(--accent-hover)] transition-colors mb-6">
          <Plus size={16} /> Создать ключ
        </button>
        {showForm && (
          <div className="bg-[var(--bg-secondary)] p-6 rounded-xl border border-[var(--border)] mb-6">
            <input type="text" placeholder="Название ключа" value={name} onChange={(e) => setName(e.target.value)}
              className="w-full p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-white text-sm focus:outline-none focus:border-[var(--accent)]" />
            <button onClick={handleCreate} className="mt-3 px-4 py-2 rounded-lg bg-[var(--accent)] text-white text-sm font-medium">Сохранить</button>
          </div>
        )}
        {keys.map((key) => (
          <div key={key.id} className="flex items-center justify-between p-4 bg-[var(--bg-secondary)] rounded-xl border border-[var(--border)]">
            <span className="text-white">{key.name}</span>
            <button onClick={async () => { await api.delete("/keys/" + key.id); setKeys(keys.filter(k => k.id !== key.id)); }} className="text-[var(--text-secondary)] hover:text-[var(--danger)]">
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
