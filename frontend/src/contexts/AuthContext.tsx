import type React from "react"
import { createContext, useContext } from "react"
import { useAuthRepository } from "@/hooks/useAuthRepository"
import { User } from "@/repositories/authRepository"

interface AuthContextType {
  user: User | null
  loading: boolean
  login: () => void
  loginWithGithub: () => void
  logout: () => Promise<{ success: boolean, error?: string }>
  refreshUser: (forceRefresh?: boolean) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { 
    user, 
    loading, 
    login,
    loginWithGithub, 
    logout,
    fetchCurrentUser 
  } = useAuthRepository()

  const value: AuthContextType = {
    user,
    loading,
    login,
    loginWithGithub,
    logout,
    refreshUser: fetchCurrentUser
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}