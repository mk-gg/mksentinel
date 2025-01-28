import { useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "./ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { useAuth } from "../contexts/AuthContext"

function Login() {
  const { login, user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (user) {
      navigate("/")
    }
  }, [user, navigate])

  return (
    <div>
      <Card className="w-[350px] mx-auto mt-10">
        <CardHeader>
          <CardTitle>Welcome to Sentinel</CardTitle>
        </CardHeader>
        <CardContent>
          <Button onClick={login} variant="outline">
            Login with Google
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

export default Login

