import SeverityBadge from "./SeverityBadge"

export default function IncidentCard({ incident }) {
  const borderColors = [
    "border-l-green-400",
    "border-l-yellow-400",
    "border-l-orange-400",
    "border-l-red-500",
  ]
  return (
    <div className={`bg-white border border-gray-200 border-l-4
                     ${borderColors[incident.severity]}
                     rounded-xl p-4 flex items-start gap-4`}>
      <div className="flex-1 min-w-0">
        <p className="text-gray-800 text-sm leading-relaxed">{incident.text}</p>
        <div className="flex gap-4 mt-2 text-xs text-gray-400">
          <span>{incident.platform}</span>
          <span>{new Date(incident.timestamp).toLocaleString()}</span>
          {incident.alert_sent && (
            <span className="text-orange-500">Alert sent</span>
          )}
        </div>
      </div>
      <SeverityBadge severity={incident.severity} label={incident.label} />
    </div>
  )
}