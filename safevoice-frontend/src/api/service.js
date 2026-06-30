import axios from "axios"

const API = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
})

// Classify a single piece of text
export const classifyText = async (text, platform = "dashboard") => {
  const res = await API.post("/classify", { text, platform })
  return res.data
}

// Get recent incidents
export const getIncidents = async (limit = 50) => {
  const res = await API.get(`/incidents?limit=${limit}`)
  return res.data
}

// Mark incident as reviewed
export const markReviewed = async (id) => {
  const res = await API.patch(`/incidents/${id}/review`)
  return res.data
}

export default API