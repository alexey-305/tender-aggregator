c = open("frontend/src/components/TenderList.jsx", "r", encoding="utf-8").read()

old_strip = '<div className="w-1 flex-shrink-0 bg-[var(--accent)]" style={{ opacity: selectedId === tender.id ? 1 : 0 }} />'

new_strip = '''{(() => {
  const marks = tender._marks || [];
  const markColor = marks.length > 0 ? marks[0].color : "transparent";
  return <div className="w-1.5 flex-shrink-0 rounded-r" style={{ 
    background: markColor !== "transparent" ? "linear-gradient(180deg, " + markColor + "80 0%, " + markColor + " 100%)" : "transparent",
    opacity: selectedId === tender.id ? 1 : 0.4,
    boxShadow: markColor !== "transparent" ? "0 0 8px " + markColor + "40" : "none"
  }} />;
})()}'''

c = c.replace(old_strip, new_strip)
open("frontend/src/components/TenderList.jsx", "w", encoding="utf-8").write(c)
print("OK")