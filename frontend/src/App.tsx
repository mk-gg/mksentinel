import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom"
import { LoginPage } from "./features/login/LoginPage"
import { HomePage } from "./pages/HomePage"
import { Bans } from "./features/bans/Bans"
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
    return null // Return nothing during initial auth check
  }

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" /> : <LoginPage />} />
      <Route path="/" element={user ? <HomePage /> : <Navigate to="/login" />} />
      <Route path="/bans" element={user ? <Bans /> : <Navigate to="/login" />} />
    </Routes>
  )
}

export default App

