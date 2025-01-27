import type React from "react"
import { createContext, useState, useEffect, useContext } from "react"
import { BASE_URL } from "@/config/api"

interface User {
  id: number
  username: string
  email: string
  is_admin: boolean
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: () => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchUserData = async () => {
    try {
      const response = await fetch(`${BASE_URL}/current_user`, {
        credentials: "include",
      })
      const data = await response.json()
      if (data.user) {
        setUser(data.user)
      }
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUserData()
  }, []) //Fixed: Added empty dependency array to useEffect

  const login = () => {
    window.location.href = `${BASE_URL}/authorize/google`
  }

  const logout = async () => {
    try {
      const response = await fetch(`${BASE_URL}/logout`, {
        credentials: "include",
      })
      const data = await response.json()
      if (data.status === "success") {
        setUser(null)
      } else {
        throw new Error(data.message)
      }
    } catch (error) {
      console.error(error)
    }
  }

  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

