const CONFIG = {
  0: { label: "Safe",       bg: "#EAF3DE", color: "#27500A", dot: "#1D9E75" },
  1: { label: "Mild",       bg: "#FAEEDA", color: "#633806", dot: "#FAC775" },
  2: { label: "Hate",       bg: "#FEF3E2", color: "#854F0B", dot: "#EF9F27" },
  3: { label: "Severe",     bg: "#FCEBEB", color: "#A32D2D", dot: "#E24B4A" },
}

export default function SeverityBadge({ severity, label }) {
  const c = CONFIG[severity] ?? CONFIG[0]
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 5,
      background: c.bg, color: c.color,
      fontSize: 11, fontWeight: 600,
      padding: "3px 9px", borderRadius: 8,
      flexShrink: 0,
    }}>
      <span style={{ width: 5, height: 5, borderRadius: "50%", background: c.dot, flexShrink: 0 }}/>
      {label ?? c.label}
    </span>
  )
}