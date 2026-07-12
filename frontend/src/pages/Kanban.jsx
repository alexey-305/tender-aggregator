import { useState, useEffect } from "react";
import { DndContext, closestCenter, PointerSensor, useSensor, useSensors } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy, useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { ArrowLeft, Plus, GripVertical, MapPin, Clock } from "lucide-react";
import api from "../api/client";
import { useNavigate } from "react-router-dom";

const COLUMNS = [
  { id: "new", title: "Новые", color: "bg-blue-500" },
  { id: "analysis", title: "Анализируем", color: "bg-yellow-500" },
  { id: "preparation", title: "Готовим заявку", color: "bg-purple-500" },
  { id: "submitted", title: "Подано", color: "bg-green-500" },
  { id: "won", title: "Победа", color: "bg-emerald-400" },
  { id: "lost", title: "Проигрыш", color: "bg-red-500" },
];

function SortableCard({ tender, onSelect }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: tender.id });
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };
  const price = tender.initial_price ? Number(tender.initial_price).toLocaleString("ru-RU") : "";

  return (
    <div ref={setNodeRef} style={style} {...attributes} onClick={() => onSelect(tender)}
      className="bg-[var(--bg-tertiary)] p-3 rounded-xl border border-[var(--border)] cursor-pointer hover:border-[var(--accent)]/50 transition-colors group">
      <div className="flex items-start gap-2">
        <button {...listeners} className="mt-0.5 text-[var(--text-secondary)] hover:text-white opacity-0 group-hover:opacity-100 transition-opacity cursor-grab">
          <GripVertical size={14} />
        </button>
        <div className="flex-1 min-w-0">
          <h4 className="text-xs font-medium text-white line-clamp-2 mb-1.5">{tender.title}</h4>
          <div className="flex items-center gap-2 text-[10px] text-[var(--text-secondary)]">
            {price && <span className="font-semibold text-white">{price} RUB</span>}
            {tender.region && <span className="flex items-center gap-0.5"><MapPin size={10} /> {tender.region}</span>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Kanban() {
  const [tenders, setTenders] = useState([]);
  const [columns, setColumns] = useState({
    new: [], analysis: [], preparation: [], submitted: [], won: [], lost: [],
  });
  const [selectedTender, setSelectedTender] = useState(null);
  const navigate = useNavigate();

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

  useEffect(() => {
    api.get("/tenders?limit=50").then((res) => {
      setTenders(res.data);
      const cols = { new: [], analysis: [], preparation: [], submitted: [], won: [], lost: [] };
      res.data.forEach((t, i) => {
        const keys = Object.keys(cols);
        cols[keys[i % keys.length]].push(t);
      });
      setColumns(cols);
    }).catch(() => {});
  }, []);

  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (!over) return;
    const activeId = active.id;
    const overId = over.id;
    
    let sourceCol = null, destCol = null;
    for (const [colId, items] of Object.entries(columns)) {
      if (items.find((t) => t.id === activeId)) sourceCol = colId;
      if (items.find((t) => t.id === overId)) destCol = colId;
    }
    if (!sourceCol || !destCol) {
      for (const colId of Object.keys(columns)) {
        if (colId === overId) destCol = colId;
      }
    }
    if (!destCol || sourceCol === destCol) return;

    const newCols = { ...columns };
    const item = newCols[sourceCol].find((t) => t.id === activeId);
    newCols[sourceCol] = newCols[sourceCol].filter((t) => t.id !== activeId);
    if (item) {
      newCols[destCol] = [...newCols[destCol], item];
    }
    setColumns(newCols);
  };

  return (
    <div className="h-screen flex flex-col bg-[var(--bg-primary)]">
      <div className="flex items-center justify-between p-4 border-b border-[var(--border)]">
        <button onClick={() => navigate("/")} className="flex items-center gap-2 text-[var(--text-secondary)] hover:text-white transition-colors">
          <ArrowLeft size={18} /> Назад
        </button>
        <h1 className="text-lg font-bold text-white">Kanban-доска</h1>
        <div className="w-20" />
      </div>

      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <div className="flex-1 flex gap-4 p-4 overflow-x-auto">
          {COLUMNS.map((col) => (
            <div key={col.id} className="flex-shrink-0 w-72 flex flex-col">
              <div className="flex items-center justify-between mb-3 px-1">
                <div className="flex items-center gap-2">
                  <div className={"w-2.5 h-2.5 rounded-full " + col.color} />
                  <h2 className="text-sm font-semibold text-white">{col.title}</h2>
                  <span className="text-xs text-[var(--text-secondary)]">{columns[col.id]?.length || 0}</span>
                </div>
                <button className="p-1 rounded hover:bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-white transition-colors">
                  <Plus size={14} />
                </button>
              </div>
              <SortableContext items={columns[col.id]?.map((t) => t.id) || []} strategy={verticalListSortingStrategy} id={col.id}>
                <div className="flex-1 space-y-2 overflow-y-auto">
                  {columns[col.id]?.map((tender) => (
                    <SortableCard key={tender.id} tender={tender} onSelect={setSelectedTender} />
                  ))}
                </div>
              </SortableContext>
            </div>
          ))}
        </div>
      </DndContext>
    </div>
  );
}