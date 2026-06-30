import { useEffect, useState } from "react"
import { getIncidents, markReviewed } from "../api/service"
import SeverityBadge from "../components/SeverityBadge"

export default function ModeratorPanel() {
  const [incidents, setIncidents] = useState([])
  const [selected,  setSelected]  = useState(new Set())
  const [loading,   setLoading]   = useState(true)
  const [error,     setError]     = useState(null)
  const [refresh,   setRefresh]   = useState(0)   // Fix 2: trigger refetch

  useEffect(() => {
    // Fix 1: defined inside effect — setState is async, not synchronous
    const fetchIncidents = async () => {
      try {
        const data = await getIncidents(200)
        setIncidents(data.filter(i => !i.reviewed))
        setError(null)
      } catch (e) {
        console.error("Failed to fetch incidents", e)
        setError("Could not load incidents. Is the backend running?")
      } finally {
        setLoading(false)
      }
    }

    fetchIncidents()
  }, [refresh])  // re-runs whenever refresh counter changes

  const toggleSelect = (id) => {
    setSelected(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const selectAll = () => setSelected(new Set(incidents.map(i => i.id)))
  const clearAll  = () => setSelected(new Set())

  const handleApprove = async () => {
    for (const id of selected) {
      await markReviewed(id).catch(() => {})
    }
    setSelected(new Set())
    setRefresh(r => r + 1)   // Fix 2: trigger useEffect to refetch
  }

  // Fix 4: revoke object URL after click to prevent memory leak
  const exportCSV = () => {
    const rows = [
      ["ID", "Text", "Platform", "Label", "Severity", "Timestamp"],
      ...incidents.map(i => [
        i.id, `"${i.text}"`, i.platform,
        i.label, i.severity, i.timestamp
      ])
    ]
    const csv  = rows.map(r => r.join(",")).join("\n")
    const blob = new Blob([csv], { type: "text/csv" })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement("a")
    a.href     = url
    a.download = "safevoice_incidents.csv"
    a.click()
    URL.revokeObjectURL(url)   // Fix 4: free memory immediately after click
  }

  return (
    <div className="max-w-5xl mx-auto p-6">

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-800">Moderator Panel</h1>
          <p className="text-gray-500">{incidents.length} unreviewed incidents</p>
        </div>
        <div className="flex gap-2">
          <button onClick={selectAll}
            className="px-3 py-1 text-sm border rounded-lg hover:bg-gray-50">
            Select all
          </button>
          <button onClick={clearAll}
            className="px-3 py-1 text-sm border rounded-lg hover:bg-gray-50">
            Clear
          </button>
          <button onClick={handleApprove} disabled={selected.size === 0}
            className="px-4 py-1 text-sm bg-green-600 text-white rounded-lg
                       disabled:opacity-40 hover:bg-green-700">
            Mark reviewed ({selected.size})
          </button>
          <button onClick={exportCSV}
            className="px-4 py-1 text-sm bg-purple-600 text-white rounded-lg
                       hover:bg-purple-700">
            Export CSV
          </button>
        </div>
      </div>

      {/* Fix 3: show error if fetch failed */}
      {error && (
        <p className="text-red-500 text-sm text-center mb-4">{error}</p>
      )}

      {loading ? (
        <p className="text-gray-400 text-center py-12">Loading...</p>
      ) : incidents.length === 0 ? (
        <p className="text-gray-400 text-center py-12">No unreviewed incidents</p>
      ) : (
        <div className="space-y-2">
          {incidents.map(incident => (
            <div key={incident.id}
              className={`flex items-start gap-3 p-4 rounded-xl border transition
                ${selected.has(incident.id)
                  ? "border-purple-400 bg-purple-50"
                  : "border-gray-200 bg-white hover:border-gray-300"}`}
            >
              <input type="checkbox"
                checked={selected.has(incident.id)}
                onChange={() => toggleSelect(incident.id)}
                className="mt-1 w-4 h-4 accent-purple-600"
              />
              <div className="flex-1 min-w-0">
                <p className="text-gray-800 text-sm">{incident.text}</p>
                <div className="flex gap-3 mt-2 text-xs text-gray-400">
                  <span>{incident.platform}</span>
                  <span>{new Date(incident.timestamp).toLocaleString()}</span>
                </div>
              </div>
              <SeverityBadge severity={incident.severity} label={incident.label} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
