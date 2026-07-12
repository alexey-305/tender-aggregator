import { Bell, User } from "lucide-react";

export default function Header() {
  return (
    <header className="h-14 bg-[var(--bg-secondary)] border-b border-[var(--border)] flex items-center justify-between px-6 flex-shrink-0">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-bold text-[var(--accent)]">TenderOS</h1>
      </div>
      <div className="flex items-center gap-4">
        <div className="relative">
          <Bell size={20} className="text-[var(--text-secondary)] hover:text-white cursor-pointer transition-colors" />
          <span className="absolute -top-1.5 -right-1.5 bg-[var(--danger)] text-white text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center">619</span>
        </div>
        <div className="w-8 h-8 rounded-full bg-[var(--accent)] flex items-center justify-center cursor-pointer hover:bg-[var(--accent-hover)] transition-colors">
          <User size={16} className="text-white" />
        </div>
      </div>
    </header>
  );
}