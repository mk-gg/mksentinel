import { Button } from "./ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { useAuth } from "../contexts/AuthContext"

function Login() {
  const { login } = useAuth()

  return (
    <div>
      <Card className="w-[350px] mx-auto mt-10">
        <CardHeader>
          <CardTitle>Google OAuth Login</CardTitle>
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

