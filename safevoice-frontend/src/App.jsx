import { BrowserRouter, Routes, Route } from "react-router-dom"
import Navbar           from "./components/Navbar"
import Dashboard        from "./pages/Dashboard"
import GuardianPortal   from "./pages/GuardianPortal"
import ModeratorPanel   from "./pages/ModeratorPanel"
import ClassifyTest     from "./pages/ClassifyTest"

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh", background: "#F8F7FF" }}>
        <Navbar />
        <main style={{ flex: 1, overflow: "auto" }}>
          <Routes>
            <Route path="/"          element={<Dashboard />}      />
            <Route path="/guardian"  element={<GuardianPortal />} />
            <Route path="/moderator" element={<ModeratorPanel />} />
            <Route path="/test"      element={<ClassifyTest />}   />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}