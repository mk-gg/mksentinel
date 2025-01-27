import { useNavigate } from "react-router-dom"
import { Button } from "./ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { useState, useEffect } from "react"
import { HomePage } from "./Homepage"
import { BASE_URL } from "@/config/api"

interface User {
  id: number
  username: string
  email: string
  is_admin: boolean
}

function Login() {
  const [user, setUser] = useState<User | null>(null)
  const navigate = useNavigate()

  const fetchUserData = async () => {
    try {
      const response = await fetch(`${BASE_URL}/current_user`, {
        // const response = await fetch('http://localhost:5000/current_user', {
        credentials: "include",
      })
      const data = await response.json()
      if (data.user) {
        setUser(data.user)
      }
    } catch (error) {
      console.error(error)
    }
  }

  // Call this on component mount
  useEffect(() => {
    fetchUserData()
  }, [])

  const handleLogin = async () => {
    try {
      window.location.href = `${BASE_URL}/authorize/google`
      // window.location.href = 'http://localhost:5000/authorize/google'
    } catch (error) {
      console.error(error)
    }
  }

  const handleLogout = async () => {
    try {
      const response = await fetch(`${BASE_URL}/logout`, {
        // const response = await fetch('http://localhost:5000/logout', {
        credentials: "include",
      })
      const data = await response.json()
      if (data.status === "success") {
        setUser(null)
        navigate("/")
      } else {
        throw new Error(data.message)
      }
    } catch (error) {
      console.error(error)
    }
  }

  if (user) {
    return <HomePage user={user} onLogout={handleLogout} />
  }

  return (
    <div>
      <Card className="w-[350px] mx-auto mt-10">
        <CardHeader>
          <CardTitle>Google OAuth Login</CardTitle>
        </CardHeader>
        <CardContent>
          <Button onClick={handleLogin} variant="outline">
            Login with Google
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

export default Login

