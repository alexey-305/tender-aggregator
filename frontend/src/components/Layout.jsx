import { useState, useEffect } from "react";
import Sidebar from "./Sidebar";
import TenderList from "./TenderList";
import TenderCard from "./TenderCard";
import KanbanBar from "./KanbanBar";
import SettingsPage from "../pages/Settings";
import api from "../api/client";

export default function Layout() {
  const [selectedTender, setSelectedTender] = useState(null);
  const [activeKey, setactiveKey] = useState(null);
  const [tenders, setTenders] = useState([]);
  const [tenderMarks, setTenderMarks] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('tenderMarks') || '{}');
    } catch {
      return {};
    }
  });
  const [page, setPage] = useState('dashboard'); // 'dashboard' | 'settings'

  useEffect(() => {
    api.get("/tenders?limit=60")
      .then((res) => setTenders(res.data))
      .catch(() => {});
  }, []);

  const handleSelectTender = (tender) => {
    setSelectedTender(tender);
    setPage('dashboard');
  };

  const handleMarksChange = (tenderId, marks) => {
    setTenderMarks(prev => {
      const updated = { ...prev, [tenderId]: marks };
      localStorage.setItem('tenderMarks', JSON.stringify(updated));
      return updated;
    });
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[var(--bg-primary)]">
      <div className="w-[296px] flex-shrink-0">
        <Sidebar
          onSelectKey={setactiveKey}
          onNavigate={(p) => setPage(p)}
        />
      </div>
      <div className="flex-1 flex flex-col min-w-0">
        {page === 'dashboard' && (
          <KanbanBar
            tenders={tenders}
            onSelectTender={handleSelectTender}
            tenderMarks={tenderMarks}
          />
        )}
        <div className="flex flex-1 overflow-hidden">
          {page === 'dashboard' ? (
            <>
              <div className="w-[481px] flex-shrink-0 border-r border-[var(--border)]">
                <TenderList
                  onSelect={handleSelectTender}
                  selectedId={selectedTender?.id}
                  activeKey={activeKey}
                  tenderMarks={tenderMarks}
                  tenders={tenders}
                />
              </div>
              <div className="flex-1 min-w-0">
                <TenderCard
                  tender={selectedTender}
                  onMarksChange={handleMarksChange}
                  currentMarks={(selectedTender && tenderMarks[selectedTender.id]) || []}
                />
              </div>
            </>
          ) : (
            <div className="flex-1 overflow-y-auto">
              <SettingsPage />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}