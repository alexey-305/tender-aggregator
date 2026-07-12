import { Inbox, FileText, Clock, CheckCircle } from "lucide-react";

const STATS = [
  { icon: Inbox, label: "НОВЫЕ ЗАКУПКИ", count: 36, sum: "5 983 929", color: "text-blue-400", bg: "bg-blue-400/10" },
  { icon: FileText, label: "ПОДГОТОВКА ЗАЯВКИ", count: 30, sum: "18 318 377", color: "text-yellow-400", bg: "bg-yellow-400/10" },
  { icon: Clock, label: "ПОДВЕДЕНИЕ ИТОГОВ", count: 62, sum: "21 280 297", color: "text-purple-400", bg: "bg-purple-400/10" },
  { icon: CheckCircle, label: "ЗАКЛЮЧЕНИЕ КОНТРАКТА", count: 1, sum: "141 000", color: "text-green-400", bg: "bg-green-400/10" },
];

export default function StatsWidgets() {
  return (
    <div className="grid grid-cols-4 gap-4 px-6 py-4 bg-[var(--bg-primary)] flex-shrink-0">
      {STATS.map((stat) => {
        const Icon = stat.icon;
        return (
          <div key={stat.label} className={"p-4 rounded-xl border border-[var(--border)] cursor-pointer hover:border-[var(--accent)] transition-colors " + stat.bg}>
            <div className="flex items-center gap-2 mb-3">
              <Icon size={20} className={stat.color} />
              <span className="text-xs font-semibold text-[var(--text-secondary)]">{stat.label}</span>
            </div>
            <div className="text-2xl font-bold text-white">{stat.count}</div>
            <div className="text-sm text-[var(--text-secondary)] mt-1">{stat.sum} RUB</div>
          </div>
        );
      })}
    </div>
  );
}