import { Header } from "./Header"
import { Footer } from "./Footer"
import { BanStatistics } from "./BanStatistics"
import { BanChart } from "./BanChart"
import { useAuth } from "../contexts/AuthContext"

export function HomePage() {
  const { user } = useAuth()

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-4">Welcome, {user?.username}!</h1>
        <p>This is your homepage. You can add more content here.</p>
        <BanStatistics />
        <BanChart />
      </main>
      <Footer />
    </div>
  )
}

