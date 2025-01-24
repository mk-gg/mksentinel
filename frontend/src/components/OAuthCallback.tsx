import type React from "react"
import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useToast } from "@/hooks/use-toast"

interface User {
  id: number
  username: string
  email: string
  is_admin: boolean
}

interface OAuthCallbackProps {
  onLogin: (user: User) => void
}

const OAuthCallback: React.FC<OAuthCallbackProps> = ({ onLogin }) => {
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const { toast } = useToast()

  useEffect(() => {
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search)
      const code = urlParams.get("code")
      const state = urlParams.get("state")

      if (code && state) {
        try {
          const response = await fetch(`/api/callback/google?code=${code}&state=${state}`, {
            credentials: "include",
          })
          const data = await response.json()

          if (data.status === "success") {
            onLogin(data.data)
            toast({
              title: "Success",
              description: "Logged in successfully",
            })
          } else {
            throw new Error(data.message)
          }
        } catch (error) {
          toast({
            title: "Error",
            description: error instanceof Error ? error.message : "An error occurred during login",
            variant: "destructive",
          })
        }
      } else {
        toast({
          title: "Error",
          description: "Invalid callback parameters",
          variant: "destructive",
        })
      }

      setLoading(false)
      navigate("/")
    }

    handleCallback()
  }, [navigate, toast, onLogin])

  if (loading) {
    return <div>Loading...</div>
  }

  return null
}

export default OAuthCallback

