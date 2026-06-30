import { Link, useLocation } from "react-router-dom"

const NAV = [
  {
    section: "Overview",
    items: [
      { to: "/",          label: "Dashboard",    icon: "grid"    },
      { to: "/guardian",  label: "Live feed",    icon: "clock"   },
    ]
  },
  {
    section: "Moderation",
    items: [
      { to: "/moderator", label: "Incidents",    icon: "file"    },
      { to: "/test",      label: "Classify text",icon: "search"  },
    ]
  }
]

const Icon = ({ name, active }) => {
  const c = active ? "#534AB7" : "#888780"
  const icons = {
    grid:   <><rect x="2" y="2" width="5" height="5" rx="1" fill={c}/><rect x="9" y="2" width="5" height="5" rx="1" fill={c} opacity=".5"/><rect x="2" y="9" width="5" height="5" rx="1" fill={c} opacity=".5"/><rect x="9" y="9" width="5" height="5" rx="1" fill={c} opacity=".5"/></>,
    clock:  <><circle cx="8" cy="8" r="5.5" stroke={c} strokeWidth="1.3" fill="none"/><path d="M8 5v3l2 1.5" stroke={c} strokeWidth="1.3" strokeLinecap="round" fill="none"/></>,
    file:   <><path d="M3 2h7l3 3v9H3V2z" stroke={c} strokeWidth="1.3" strokeLinejoin="round" fill="none"/><path d="M10 2v3h3M5 7h6M5 10h4" stroke={c} strokeWidth="1.3" strokeLinecap="round" fill="none"/></>,
    search: <><circle cx="7" cy="7" r="4.5" stroke={c} strokeWidth="1.3" fill="none"/><path d="M10.5 10.5L14 14" stroke={c} strokeWidth="1.3" strokeLinecap="round" fill="none"/></>,
  }
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      {icons[name]}
    </svg>
  )
}

export default function Navbar() {
  const { pathname } = useLocation()
  return (
    <aside style={{
      width: 220,
      background: "#fff",
      borderRight: "0.5px solid #E8E6F0",
      display: "flex",
      flexDirection: "column",
      flexShrink: 0,
      padding: "20px 0",
      minHeight: "100vh",
    }}>
      {/* Logo */}
      <div style={{ padding: "0 18px 24px", display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{
          width: 32, height: 32, borderRadius: 10,
          background: "#534AB7",
          display: "flex", alignItems: "center", justifyContent: "center",
          flexShrink: 0,
        }}>
          <svg width="18" height="18" viewBox="0 0 16 16" fill="none">
            <path d="M8 2L3 5v4c0 2.5 2 4.5 5 5 3-.5 5-2.5 5-5V5L8 2z" fill="white" opacity=".9"/>
            <path d="M6 8l1.5 1.5L10 6.5" stroke="#534AB7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        <div>
          <div style={{ fontSize: 15, fontWeight: 600, color: "#1a1a2e" }}>SafeVoice</div>
          <div style={{ fontSize: 10, color: "#888780", marginTop: 1 }}>AI Content Shield</div>
        </div>
      </div>

      {/* Nav sections */}
      {NAV.map(group => (
        <div key={group.section} style={{ marginBottom: 8 }}>
          <div style={{
            padding: "8px 18px 4px",
            fontSize: 10, fontWeight: 600,
            color: "#B4B2A9",
            textTransform: "uppercase", letterSpacing: "0.07em"
          }}>
            {group.section}
          </div>
          {group.items.map(item => {
            const active = pathname === item.to
            return (
              <Link key={item.to} to={item.to} style={{ textDecoration: "none" }}>
                <div style={{
                  display: "flex", alignItems: "center", gap: 10,
                  padding: "9px 18px",
                  fontSize: 13,
                  fontWeight: active ? 500 : 400,
                  color: active ? "#534AB7" : "#5F5E5A",
                  background: active ? "#F0EFFE" : "transparent",
                  borderLeft: `2px solid ${active ? "#534AB7" : "transparent"}`,
                  transition: "all 0.15s",
                  cursor: "pointer",
                }}>
                  <Icon name={item.icon} active={active} />
                  {item.label}
                </div>
              </Link>
            )
          })}
        </div>
      ))}

      {/* Bottom status */}
      <div style={{ marginTop: "auto", padding: "16px 18px 0" }}>
        <div style={{
          background: "#EEEDFE", borderRadius: 10, padding: "10px 12px"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
            <div style={{
              width: 7, height: 7, borderRadius: "50%",
              background: "#1D9E75",
              animation: "pulse 2s infinite",
            }}/>
            <span style={{ fontSize: 12, fontWeight: 500, color: "#3C3489" }}>System active</span>
          </div>
          <div style={{ fontSize: 11, color: "#7F77DD" }}>
            Tamil · Hindi · English detection online
          </div>
        </div>
      </div>

      <style>{`@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}`}</style>
    </aside>
  )
}