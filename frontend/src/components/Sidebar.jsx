import { useState, useEffect } from "react";
import { Bell, Key, Users, BarChart3, Settings, Trash2, ChevronUp, ChevronDown, Plus } from "lucide-react";

import api from "../api/client";

export default function Sidebar({ onSelectKey, onNavigate }) {
  const [keys, setKeys] = useState([]);
  const [keysExpanded, setKeysExpanded] = useState(true);
  const [usersExpanded, setUsersExpanded] = useState(true);
  

  useEffect(() => {
    api.get("/keys").then(res => setKeys(res.data)).catch(() => {});
  }, []);

  return (
    <div className="h-screen bg-[var(--bg-secondary)] flex flex-col border-r border-[var(--border)]">
      <div className="p-4 border-b border-[var(--border)]">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-[var(--accent)] flex items-center justify-center">
            <span className="text-white font-bold text-sm">T</span>
          </div>
          <span className="text-lg font-bold text-white">TenderOS</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
          <div className="w-6 h-6 rounded-full bg-[var(--bg-tertiary)] flex items-center justify-center text-[10px] text-white">U</div>
          <span className="truncate text-xs">Пользователь</span>
        </div>
      </div>

      <div className="px-3 !py-4 border-b border-[var(--border)]">
        <div className="flex items-center justify-between p-2 rounded-lg bg-[var(--accent)]/10 cursor-pointer hover:bg-[var(--accent)]/20 transition-colors">
          <div className="flex items-center gap-2">
            <Bell size={16} className="text-[var(--accent)]" />
            <span className="text-sm text-white">Уведомления</span>
          </div>
          <span className="text-sm font-bold text-[var(--accent)]">0</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="px-3 !py-2">
          <div className="flex items-center justify-between cursor-pointer !py-1" onClick={() => { setKeysExpanded(!keysExpanded); onNavigate && onNavigate('dashboard'); }}>
            <div className="flex items-center gap-2">
              <Key size={14} className="text-[var(--text-secondary)]" />
              <span className="text-xs font-semibold text-[var(--text-secondary)] uppercase">Шаблоны</span>
            </div>
            <div className="flex items-center gap-1">
              <button onClick={(e) => { e.stopPropagation(); onNavigate && onNavigate("settings"); }} className="p-0.5 rounded hover:bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-white transition-colors" title="Добавить шаблон">
                <Plus size={14} />
              </button>
              {keysExpanded ? <ChevronUp size={14} className="text-[var(--text-secondary)]" /> : <ChevronDown size={14} className="text-[var(--text-secondary)]" />}
            </div>
          </div>
          {keysExpanded && (
            <div className="mt-1">
              {keys.length === 0 ? (
                <div className="text-xs text-[var(--text-secondary)] px-2 py-3 text-center">Нет шаблонов. Нажмите + чтобы создать.</div>
              ) : (
                <div className="space-y-6">
                  {keys.map((key) => (
                    <div key={key.id} onClick={() => onSelectKey && onSelectKey(key)} className="flex items-center justify-between px-2 !!py-1.5 rounded cursor-pointer text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] hover:text-white">
                      <span className="truncate text-xs">{key.name}</span>
                      <span className="text-xs ml-2">{key.count || 0}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="px-6 py-5">
          <div className="flex items-center justify-between cursor-pointer !py-1" onClick={() => { setUsersExpanded(!usersExpanded); onNavigate && onNavigate('dashboard'); }}>
            <div className="flex items-center gap-2">
              <Users size={14} className="text-[var(--text-secondary)]" />
              <span className="text-xs font-semibold text-[var(--text-secondary)] uppercase">Пользователи</span>
            </div>
            {usersExpanded ? <ChevronUp size={14} className="text-[var(--text-secondary)]" /> : <ChevronDown size={14} className="text-[var(--text-secondary)]" />}
          </div>
          {usersExpanded && (
            <div className="mt-1">
              <div className="text-xs text-[var(--text-secondary)] px-2 py-3 text-center">Добавьте пользователей в настройках.</div>
            </div>
          )}
        </div>
      </div>

      <div className="p-3 border-t border-[var(--border)] space-y-1">
        <div className="flex items-center gap-2 px-2 !!py-1.5 rounded cursor-pointer text-xs text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] hover:text-white">
          <BarChart3 size={14} /> Аналитика
        </div>
        <div onClick={() => onNavigate && onNavigate("settings")} className="flex items-center gap-2 px-2 !!py-1.5 rounded cursor-pointer text-xs text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] hover:text-white">
          <Settings size={14} /> Настройки
        </div>
        <div className="flex items-center gap-2 px-2 !!py-1.5 rounded cursor-pointer text-xs text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] hover:text-white">
          <Trash2 size={14} /> Корзина
        </div>
      </div>
    </div>
  );
}