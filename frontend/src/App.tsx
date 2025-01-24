import type React from "react"
import { useState } from "react"
import { BrowserRouter as Router, Route, Routes } from "react-router-dom"
import Header from "./components/Header"
import Footer from "./components/Footer"
import Homepage from "./components/Homepage"
import Login from "./components/Login"
import OAuthCallback from "./components/OAuthCallback"
import { Toaster } from "@/components/ui/toaster"

interface User {
  id: number
  username: string
  email: string
  is_admin: boolean
}

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null)

  const handleLogin = (loggedInUser: User) => {
    setUser(loggedInUser)
  }

  const handleLogout = async () => {
    try {
      const response = await fetch("/api/logout")
      const data = await response.json()
      if (data.status === "success") {
        setUser(null)
      } else {
        throw new Error(data.message)
      }
    } catch (error) {
      console.error("Logout error:", error)
    }
  }

  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        {user && <Header username={user.username} onLogout={handleLogout} />}
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={user ? <Homepage /> : <Login onLogin={handleLogin} />} />
            <Route path="/callback/google" element={<OAuthCallback onLogin={handleLogin} />} />
          </Routes>
        </main>
        <Footer />
      </div>
      <Toaster />
    </Router>
  )
}

export default App

