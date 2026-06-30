import { useState } from "react"
import { classifyText } from "../api/service"
import SeverityBadge from "../components/SeverityBadge"

const SAMPLES = [
  { text: "நீங்கள் எப்படி இருக்கீங்க?",        tag: "Tamil · safe"     },
  { text: "dei stupid fellow, get out now",       tag: "English · mild"   },
  { text: "I will find you and hurt you badly",   tag: "English · severe" },
  { text: "உன்னை பாத்துக்கிறேன் நாளைக்கு",      tag: "Tamil · threat"   },
  { text: "तुम बेकार हो, यहाँ से चले जाओ",       tag: "Hindi · hate"     },
]

const SEV_COLORS = ["#1D9E75", "#FAC775", "#EF9F27", "#E24B4A"]
const SEV_BG     = ["#EAF3DE", "#FAEEDA", "#FEF3E2", "#FCEBEB"]

export default function ClassifyTest() {
  const [text,    setText]   = useState("")
  const [result,  setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]  = useState("")

  const classify = async () => {
    if (!text.trim()) return
    setLoading(true); setError(""); setResult(null)
    try {
      setResult(await classifyText(text, "dashboard"))
    } catch {
      setError("Cannot reach API — make sure backend is running on port 8000")
    } finally { setLoading(false) }
  }

  return (
    <div style={{ minHeight:"100vh", background:"#F8F7FF" }}>
      {/* Topbar */}
      <div style={{
        padding:"20px 28px", borderBottom:"0.5px solid #E8E6F0",
        background:"#fff"
      }}>
        <h1 style={{ fontSize:17, fontWeight:600, color:"#1a1a2e" }}>Classify text</h1>
        <p style={{ fontSize:12, color:"#888780", marginTop:2 }}>
          Test detection with Tamil, Hindi, or English text
        </p>
      </div>

      <div style={{ padding:"28px", maxWidth:680 }}>
        {/* Sample pills */}
        <div style={{ marginBottom:16 }}>
          <div style={{ fontSize:11, color:"#888780", marginBottom:8, textTransform:"uppercase", letterSpacing:"0.06em" }}>
            Try a sample
          </div>
          <div style={{ display:"flex", flexWrap:"wrap", gap:7 }}>
            {SAMPLES.map(s => (
              <button key={s.text} onClick={() => { setText(s.text); setResult(null) }} style={{
                fontSize:11, padding:"5px 12px", borderRadius:20,
                border:"0.5px solid #E8E6F0", background:"#fff",
                color:"#5F5E5A", cursor:"pointer", transition:"all .15s",
              }}
              onMouseOver={e => e.currentTarget.style.borderColor = "#534AB7"}
              onMouseOut={e  => e.currentTarget.style.borderColor = "#E8E6F0"}
              >
                {s.tag}
              </button>
            ))}
          </div>
        </div>

        {/* Input card */}
        <div style={{
          background:"#fff", border:"0.5px solid #E8E6F0",
          borderRadius:14, padding:"18px 20px", marginBottom:14
        }}>
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            onKeyDown={e => e.key === "Enter" && e.metaKey && classify()}
            placeholder="Type Tamil, Hindi, or English text here..."
            style={{
              width:"100%", border:"none", outline:"none",
              fontSize:14, color:"#1a1a2e", lineHeight:1.7,
              resize:"none", height:100, background:"transparent",
              fontFamily:"inherit",
            }}
          />
          <div style={{
            borderTop:"0.5px solid #E8E6F0", paddingTop:12, marginTop:4,
            display:"flex", alignItems:"center", justifyContent:"space-between"
          }}>
            <span style={{ fontSize:11, color:"#B4B2A9" }}>
              {text.length} characters · ⌘Enter to classify
            </span>
            <button onClick={classify} disabled={loading || !text.trim()} style={{
              padding:"8px 20px",
              background: loading || !text.trim() ? "#B4B2A9" : "#534AB7",
              color:"#fff", border:"none", borderRadius:8,
              fontSize:13, fontWeight:500,
              cursor: loading || !text.trim() ? "not-allowed" : "pointer",
              transition:"background .15s",
            }}>
              {loading ? "Classifying..." : "Classify"}
            </button>
          </div>
        </div>

        {error && (
          <div style={{
            background:"#FCEBEB", border:"0.5px solid #F09595",
            borderRadius:10, padding:"12px 14px",
            fontSize:13, color:"#A32D2D", marginBottom:14
          }}>
            {error}
          </div>
        )}

        {/* Result card */}
        {result && (
          <div style={{
            background: SEV_BG[result.severity] ?? "#fff",
            border:`0.5px solid #E8E6F0`,
            borderTop:`3px solid ${SEV_COLORS[result.severity]}`,
            borderRadius:14, padding:"20px 22px",
          }}>
            <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:18 }}>
              <div>
                <div style={{ fontSize:12, color:"#888780", marginBottom:4 }}>Detection result</div>
                <div style={{ fontSize:16, fontWeight:600, color:"#1a1a2e" }}>
                  {result.text.length > 60 ? result.text.slice(0, 60) + "..." : result.text}
                </div>
              </div>
              <SeverityBadge severity={result.severity} label={result.label} />
            </div>

            {/* Score bars */}
            <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
              {Object.entries(result.scores)
                .sort((a, b) => b[1] - a[1])
                .map(([label, score]) => {
                  const sev = ["safe", "mild_toxic", "hate_speech", "severe"].indexOf(label)
                  const col = SEV_COLORS[sev] ?? "#888780"
                  return (
                    <div key={label}>
                      <div style={{ display:"flex", justifyContent:"space-between", marginBottom:4, fontSize:12 }}>
                        <span style={{ color:"#5F5E5A", textTransform:"capitalize" }}>
                          {label.replace(/_/g, " ")}
                        </span>
                        <span style={{ fontWeight:500, color:"#1a1a2e" }}>{score.toFixed(1)}%</span>
                      </div>
                      <div style={{ background:"#F1EFE8", borderRadius:20, height:7, overflow:"hidden" }}>
                        <div style={{
                          width:`${score}%`, height:"100%",
                          background: col, borderRadius:20,
                          transition:"width .5s ease",
                        }}/>
                      </div>
                    </div>
                  )
                })}
            </div>

            <div style={{
              marginTop:16, paddingTop:14, borderTop:"0.5px solid #E8E6F0",
              display:"flex", gap:20, fontSize:11, color:"#B4B2A9"
            }}>
              <span>Confidence: <strong style={{ color:"#1a1a2e" }}>{result.confidence}%</strong></span>
              <span>Platform: <strong style={{ color:"#1a1a2e" }}>dashboard</strong></span>
              <span>Alert: <strong style={{ color: result.alert_sent ? "#E24B4A" : "#1D9E75" }}>
                {result.alert_sent ? "Sent" : "Not needed"}
              </strong></span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}