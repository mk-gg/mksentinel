import type React from "react"
import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"

interface User {
  id: number
  username: string
  email: string
  is_admin: boolean
}

interface LoginProps {
  onLogin: (user: User) => void
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [loading, setLoading] = useState<boolean>(false)
  const { toast } = useToast()

  useEffect(() => {
    checkUserStatus()
  }, [])

  const checkUserStatus = async () => {
    try {
      const response = await fetch("/api/user", {
        credentials: "include",
      })
      const data = await response.json()
      if (data.status === "success") {
        onLogin(data.data)
      }
    } catch (error) {
      console.error("Error checking user status:", error)
    }
  }

  const handleLogin = async () => {
    setLoading(true)
    try {
      const response = await fetch("/api/authorize/google", {
        credentials: "include",
      })
      const data = await response.json()
      if (data.status === "success") {
        window.location.href = data.data.authUrl
      } else {
        throw new Error(data.message)
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "An error occurred during login",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="w-[350px] mx-auto mt-10">
      <CardHeader>
        <CardTitle>Google OAuth Login</CardTitle>
      </CardHeader>
      <CardContent>
        <Button onClick={handleLogin} disabled={loading} className="w-full">
          {loading ? "Loading..." : "Login with Google"}
        </Button>
      </CardContent>
    </Card>
  )
}

export default Login

