import Login from "./Login"
import { Footer } from "./Footer"

export function LoginPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex-grow flex items-center justify-center">
        <Login />
      </main>
      <Footer />
    </div>
  )
}

