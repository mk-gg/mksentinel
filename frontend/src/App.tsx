import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom"
import Login from "./components/Login"
import { HomePage } from "./components/Homepage"
import { Bans } from "./components/Bans"
import { AuthProvider, useAuth } from "./contexts/AuthContext"

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  )
}

function AppRoutes() {
  const { user, loading } = useAuth()

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
      <Route path="/" element={user ? <HomePage /> : <Navigate to="/login" />} />
      <Route path="/bans" element={user ? <Bans /> : <Navigate to="/login" />} />
    </Routes>
  )
}

export default App

