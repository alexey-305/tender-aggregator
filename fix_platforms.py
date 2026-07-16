c = open("frontend/src/pages/Settings.jsx", "r", encoding="utf-8").read()
old = 'platforms.includes("Все площадки") ? "Все площадки" : platforms.filter(p => p !== "Все площадки").join(", ") || "Все площадки"'
new = '(platforms.length === 1 && platforms[0] === "Все площадки") || platforms.length === 0 ? "Все площадки" : platforms.filter(p => p !== "Все площадки").join(", ")'
c = c.replace(old, new)
open("frontend/src/pages/Settings.jsx", "w", encoding="utf-8").write(c)
print("OK")