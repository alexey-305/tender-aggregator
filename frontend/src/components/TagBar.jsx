const TAGS = [
  { name: "Все", count: 302 },
  { name: "Автобусы", count: 4 },
  { name: "Спецтехника", count: 17 },
  { name: "Запчасти", count: 6 },
  { name: "Самосвал", count: 19 },
  { name: "ХОУ", count: 217 },
  { name: "FOTON", count: 14 },
];

export default function TagBar({ activeTag, onSelect }) {
  return (
    <div className="h-10 bg-[var(--bg-secondary)] border-b border-[var(--border)] flex items-center px-6 gap-2 overflow-x-auto flex-shrink-0">
      {TAGS.map((tag) => (
        <button
          key={tag.name}
          onClick={() => onSelect(tag.name)}
          className={"px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors " + (activeTag === tag.name ? "bg-[var(--accent)] text-white" : "bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-white")}
        >
          {tag.name} {tag.count}
        </button>
      ))}
    </div>
  );
}