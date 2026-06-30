import { useEffect, useState } from "react"
import { getIncidents } from "../api/service"
import SeverityBadge from "../components/SeverityBadge"

const PLATFORM_COLORS = {
  youtube:"#E24B4A", instagram:"#D4537E",
  telegram:"#378ADD", whatsapp:"#1D9E75", unknown:"#888780"
}

export default function GuardianPortal() {
  const [incidents, setIncidents] = useState([])
  const [filter,    setFilter]    = useState("all")
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    const fetch = () => getIncidents(150).then(d => { setIncidents(d); setLoading(false) })
    fetch()
    const t = setInterval(fetch, 15000)
    return () => clearInterval(t)
  }, [])

  const filtered = filter === "all"
    ? incidents
    : incidents.filter(i => i.label === filter || String(i.severity) === filter)

  return (
    <div style={{ minHeight: "100vh", background: "#F8F7FF" }}>
      <div style={{
        padding: "20px 28px", borderBottom: "0.5px solid #E8E6F0",
        background: "#fff", display: "flex", alignItems: "center", justifyContent: "space-between"
      }}>
        <div>
          <h1 style={{ fontSize: 17, fontWeight: 600, color: "#1a1a2e" }}>Live incident feed</h1>
          <p style={{ fontSize: 12, color: "#888780", marginTop: 2 }}>
            Auto-refreshes every 15 seconds
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width:8,height:8,borderRadius:"50%",background:"#1D9E75",animation:"pulse 2s infinite" }}/>
          <span style={{ fontSize:12, color:"#0F6E56", fontWeight:500 }}>{incidents.length} monitored</span>
        </div>
        <style>{`@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}`}</style>
      </div>

      <div style={{ padding: "24px 28px", display: "flex", flexDirection: "column", gap: 16 }}>
        {/* Filter pills */}
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {[
            { key: "all",        label: "All",         count: incidents.length },
            { key: "3",          label: "Severe",      count: incidents.filter(i=>i.severity===3).length },
            { key: "hate_speech",label: "Hate speech", count: incidents.filter(i=>i.label==="hate_speech").length },
            { key: "mild_toxic", label: "Mild toxic",  count: incidents.filter(i=>i.label==="mild_toxic").length },
            { key: "safe",       label: "Safe",        count: incidents.filter(i=>i.label==="safe").length },
          ].map(f => (
            <button key={f.key} onClick={() => setFilter(f.key)} style={{
              display: "flex", alignItems: "center", gap: 6,
              padding: "6px 14px", borderRadius: 20, fontSize: 12, cursor: "pointer",
              border: filter === f.key ? "1.5px solid #534AB7" : "0.5px solid #E8E6F0",
              background: filter === f.key ? "#534AB7" : "#fff",
              color: filter === f.key ? "#fff" : "#5F5E5A",
              fontWeight: filter === f.key ? 500 : 400,
              transition: "all .15s",
            }}>
              {f.label}
              <span style={{
                background: filter === f.key ? "rgba(255,255,255,.25)" : "#EEEDFE",
                color: filter === f.key ? "#fff" : "#3C3489",
                fontSize: 10, fontWeight: 600, padding: "1px 6px", borderRadius: 10
              }}>{f.count}</span>
            </button>
          ))}
        </div>

        {/* Incident cards */}
        {loading ? (
          <div style={{ textAlign:"center", padding:48, color:"#B4B2A9" }}>Loading...</div>
        ) : filtered.length === 0 ? (
          <div style={{ textAlign:"center", padding:48, color:"#B4B2A9" }}>No incidents found</div>
        ) : (
          <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
            {filtered.map(inc => (
              <div key={inc.id} style={{
                background:"#fff", borderRadius:12,
                border:"0.5px solid #E8E6F0",
                borderLeft:`4px solid ${["#1D9E75","#FAC775","#EF9F27","#E24B4A"][inc.severity]}`,
                padding:"14px 16px", display:"flex", alignItems:"flex-start", gap:14,
              }}>
                <div style={{ flex:1 }}>
                  <p style={{ fontSize:14, color:"#1a1a2e", lineHeight:1.6, margin:0 }}>{inc.text}</p>
                  <div style={{ display:"flex", gap:14, marginTop:8, fontSize:11, color:"#B4B2A9", flexWrap:"wrap" }}>
                    <span style={{ display:"flex", alignItems:"center", gap:4 }}>
                      <span style={{ width:6,height:6,borderRadius:"50%",
                        background:PLATFORM_COLORS[inc.platform]??"#888780",display:"inline-block" }}/>
                      {inc.platform}
                    </span>
                    {inc.language && <span>{inc.language}</span>}
                    <span>{new Date(inc.timestamp).toLocaleString()}</span>
                    {inc.alert_sent && (
                      <span style={{ color:"#E24B4A", fontWeight:500 }}>Alert sent</span>
                    )}
                  </div>
                </div>
                <SeverityBadge severity={inc.severity} label={inc.label} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}