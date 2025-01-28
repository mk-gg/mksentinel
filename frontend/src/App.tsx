import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom"
import { LoginPage } from "./components/LoginPage"
import { HomePage } from "./components/Homepage"
import { Bans } from "./components/Bans"
import { AuthProvider, useAuth } from "./contexts/AuthContext"
import { Skeleton } from "@/components/ui/skeleton"

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
    return (
      <div className="flex flex-col min-h-screen p-8 space-y-4">
        <Skeleton className="h-12 w-[250px]" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-[450px]" />
          <Skeleton className="h-4 w-[400px]" />
          <Skeleton className="h-4 w-[350px]" />
        </div>
        <div className="grid gap-4 mt-8 md:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="h-4 w-[250px]" />
              <Skeleton className="h-4 w-[200px]" />
            </div>
          ))}
        </div>
      </div>
    )
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

