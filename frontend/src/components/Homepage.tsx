import { useNavigate } from "react-router-dom"
import { Header } from "./Header"
import { Footer } from "./Footer"
import { BanStatistics } from "./BanStatistics"
import { BanChart } from "./BanChart"

interface User {
  id: number
  username: string
  email: string
  is_admin: boolean
}

interface HomePageProps {
  user: User
  onLogout: () => void
}

export function HomePage({ user, onLogout }: HomePageProps) {
  const navigate = useNavigate()

  return (
    <div className="flex flex-col min-h-screen">
      <Header user={user} onLogout={onLogout} onNavigate={navigate}/>
      <main className="flex-grow container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-4">Welcome, {user.username}!</h1>
        <p>1This is your homepage. You can add more content here.</p>
        <BanStatistics />
        <BanChart />
      </main>
      <Footer />
    </div>
  )
}

