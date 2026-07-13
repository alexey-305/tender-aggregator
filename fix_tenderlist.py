with open('C:/TenderAggregator/frontend/src/components/TenderList.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

old = 'api.get("/tenders?limit=100").then((res) => { let data = res.data; if (activeKey) { data = data.filter(t => { if (activeKey.keywords && t.title && !t.title.toLowerCase().includes(activeKey.keywords.toLowerCase())) return false; if (activeKey.okpd2 && t.okpd2_codes && !t.okpd2_codes.some(c => c.includes(activeKey.okpd2))) return false; if (activeKey.region && t.region !== activeKey.region) return false; if (activeKey.law && t.law !== activeKey.law) return false; return true; }); } setTenders(data); }).catch(() => {})'

new = '''api.get(activeKey ? "/tenders/filter?keywords=" + encodeURIComponent(activeKey.keywords || "") + "&region=" + (activeKey.region || "") + "&law=" + (activeKey.law || "") + "&price_from=" + (activeKey.price_from || "") + "&price_to=" + (activeKey.price_to || "") : "/tenders?limit=100").then((res) => { setTenders(res.data); }).catch(() => {})'''

content = content.replace(old, new)
with open('C:/TenderAggregator/frontend/src/components/TenderList.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('OK')