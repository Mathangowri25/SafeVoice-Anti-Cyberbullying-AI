import { useEffect, useState } from "react"
import { getIncidents } from "../api/service"
import SeverityBadge from "../components/SeverityBadge"

const PLATFORM_COLORS = {
  youtube:   "#E24B4A",
  instagram: "#D4537E",
  telegram:  "#378ADD",
  whatsapp:  "#1D9E75",
  unknown:   "#888780",
}

const TopBar = ({ title, subtitle }) => (
  <div style={{
    padding: "20px 28px",
    borderBottom: "0.5px solid #E8E6F0",
    background: "#fff",
    display: "flex", alignItems: "center", justifyContent: "space-between",
  }}>
    <div>
      <h1 style={{ fontSize: 17, fontWeight: 600, color: "#1a1a2e" }}>{title}</h1>
      <p style={{ fontSize: 12, color: "#888780", marginTop: 2 }}>{subtitle}</p>
    </div>
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{
        width: 8, height: 8, borderRadius: "50%",
        background: "#1D9E75", animation: "pulse 2s infinite"
      }}/>
      <span style={{ fontSize: 12, color: "#0F6E56", fontWeight: 500 }}>Live monitoring</span>
    </div>
    <style>{`@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}`}</style>
  </div>
)

// Fix: removed "icon" from destructured props — it was never used in JSX
const StatCard = ({ label, value, color, sub }) => (
  <div style={{
    background: "#fff",
    border: "0.5px solid #E8E6F0",
    borderRadius: 12,
    padding: "16px 18px",
    borderTop: `3px solid ${color}`,
  }}>
    <div style={{ fontSize: 11, color: "#888780", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>
      {label}
    </div>
    <div style={{ fontSize: 28, fontWeight: 600, color, lineHeight: 1 }}>{value}</div>
    <div style={{ fontSize: 11, color: "#B4B2A9", marginTop: 6 }}>{sub}</div>
  </div>
)

export default function Dashboard() {
  const [incidents, setIncidents] = useState([])
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getIncidents(100)
        setIncidents(data)
      } catch {
        console.error("Failed to load incidents")
      } finally {
        setLoading(false)
      }
    }
    fetchData()
    const t = setInterval(async () => {
      try {
        const data = await getIncidents(100)
        setIncidents(data)
      } catch {
        // silent fail on background refresh
      }
    }, 15000)
    return () => clearInterval(t)
  }, [])

  const counts = {
    severe: incidents.filter(i => i.severity === 3).length,
    hate:   incidents.filter(i => i.severity === 2).length,
    mild:   incidents.filter(i => i.severity === 1).length,
    safe:   incidents.filter(i => i.severity === 0).length,
  }
  const recent = incidents.slice(0, 8)

  return (
    <div style={{ minHeight: "100vh", background: "#F8F7FF" }}>
      <TopBar
        title="Guardian Dashboard"
        subtitle="Real-time detection — Tamil, Hindi, English across 4 platforms"
      />

      <div style={{ padding: "24px 28px", display: "flex", flexDirection: "column", gap: 24 }}>

        {/* Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,minmax(0,1fr))", gap: 14 }}>
          <StatCard label="Severe"      value={counts.severe} color="#E24B4A" sub="Immediate action" />
          <StatCard label="Hate speech" value={counts.hate}   color="#EF9F27" sub="Review needed"    />
          <StatCard label="Mild toxic"  value={counts.mild}   color="#FAC775" sub="Monitor closely"  />
          <StatCard label="Safe"        value={counts.safe}   color="#1D9E75" sub="Total today"      />
        </div>

        {/* Platform coverage */}
        <div style={{ background: "#fff", border: "0.5px solid #E8E6F0", borderRadius: 12, padding: "18px 20px" }}>
          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 14, color: "#1a1a2e" }}>
            Platform coverage
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }}>
            {[
              { name: "YouTube",   color: "#E24B4A", desc: "Video comments",  lang: "Tamil · Hindi"   },
              { name: "Instagram", color: "#D4537E", desc: "Post comments",   lang: "Tamil · English" },
              { name: "WhatsApp",  color: "#1D9E75", desc: "Group messages",  lang: "All languages"   },
              { name: "Telegram",  color: "#378ADD", desc: "Public channels", lang: "Tamil · Hindi"   },
            ].map(p => (
              <div key={p.name} style={{
                border: "0.5px solid #E8E6F0", borderRadius: 10, padding: "12px 14px",
                borderTop: `2px solid ${p.color}`,
              }}>
                <div style={{ fontWeight: 600, fontSize: 13, color: "#1a1a2e" }}>{p.name}</div>
                <div style={{ fontSize: 11, color: "#888780", marginTop: 3 }}>{p.desc}</div>
                <div style={{
                  marginTop: 8, fontSize: 10, fontWeight: 500,
                  background: "#F8F7FF", padding: "3px 7px",
                  borderRadius: 6, display: "inline-block", color: "#5F5E5A"
                }}>
                  {p.lang}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent incidents */}
        <div style={{ background: "#fff", border: "0.5px solid #E8E6F0", borderRadius: 12, padding: "18px 20px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: "#1a1a2e" }}>Recent incidents</span>
            <span style={{
              fontSize: 11, background: "#EEEDFE", color: "#3C3489",
              padding: "3px 10px", borderRadius: 20, fontWeight: 500
            }}>
              {incidents.length} total
            </span>
          </div>

          {loading ? (
            <div style={{ textAlign: "center", padding: 32, color: "#B4B2A9", fontSize: 13 }}>
              Loading incidents...
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {recent.map((inc, idx) => (
                <div key={inc.id ?? idx} style={{
                  display: "flex", alignItems: "flex-start", gap: 12,
                  padding: "12px 14px",
                  border: "0.5px solid #E8E6F0",
                  borderLeft: `3px solid ${["#1D9E75","#FAC775","#EF9F27","#E24B4A"][inc.severity] ?? "#888780"}`,
                  borderRadius: 10,
                  background: "#FAFAFA",
                }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: 13, color: "#1a1a2e", lineHeight: 1.5, margin: 0 }}>
                      {inc.text}
                    </p>
                    <div style={{ display: "flex", gap: 12, marginTop: 6, fontSize: 11, color: "#B4B2A9" }}>
                      <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                        <span style={{
                          width: 6, height: 6, borderRadius: "50%",
                          background: PLATFORM_COLORS[inc.platform] ?? "#888780",
                          display: "inline-block"
                        }}/>
                        {inc.platform}
                      </span>
                      <span>{inc.language ?? "—"}</span>
                      <span>{new Date(inc.timestamp).toLocaleTimeString()}</span>
                      {inc.alert_sent && (
                        <span style={{ color: "#E24B4A", fontWeight: 500 }}>Alert sent</span>
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
    </div>
  )
}
