import { useState, useEffect } from "react";
import Sidebar from "./Sidebar";
import TenderList from "./TenderList";
import TenderCard from "./TenderCard";
import KanbanBar from "./KanbanBar";
import api from "../api/client";

export default function Layout() {
  const [selectedTender, setSelectedTender] = useState(null);
  const [activeKey, setActiveKey] = useState(null);
  const [activeMark, setActiveMark] = useState(null);
  const [tenders, setTenders] = useState([]);
  const [tenderMarks, setTenderMarks] = useState(() => { try { return JSON.parse(localStorage.getItem('tenderMarks') || '{}'); } catch { return {}; } });

  useEffect(() => {
    api.get("/tenders?limit=60").then((res) => setTenders(res.data)).catch(() => {});
  }, []);

  const handleSelectTender = (tender) => {
    setSelectedTender(tender);
  };

  const handleMarksChange = (tenderId, marks) => { const updated = { ...tenderMarks, [tenderId]: marks }; localStorage.setItem('tenderMarks', JSON.stringify(updated)); setTenderMarks(updated); // was: setTenderMarks(prev => ({ ...prev, [tenderId]: marks }));
    setTenderMarks(prev => ({ ...prev, [tenderId]: marks }));
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[var(--bg-primary)]">
      <div className="w-64 flex-shrink-0">
        <Sidebar onSelectKey={setActiveKey} onSelectMark={setActiveMark} activeMarkId={activeMark?.id} />
      </div>
      <div className="flex-1 flex flex-col min-w-0">
        <KanbanBar tenders={tenders} onSelectTender={handleSelectTender} tenderMarks={tenderMarks} />
        <div className="flex flex-1 overflow-hidden">
          <div className="w-[380px] flex-shrink-0 border-r border-[var(--border)]">
            <TenderList onSelect={handleSelectTender} selectedId={selectedTender?.id} activeKey={activeKey} />
          </div>
          <div className="flex-1 min-w-0">
            <TenderCard tender={selectedTender} onMarksChange={handleMarksChange} currentMarks={(selectedTender && tenderMarks[selectedTender.id]) || []} />
          </div>
        </div>
      </div>
    </div>
  );
}

