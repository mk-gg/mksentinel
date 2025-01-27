import { Header } from "./Header"
import { Footer } from "./Footer"
import { BanStatistics } from "./BanStatistics"

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
  return (
    <div className="flex flex-col min-h-screen">
      <Header user={user} onLogout={onLogout} />
      <main className="flex-grow container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-4">Welcome, {user.username}!</h1>
        <p>This is your homepage. You can add more content here.</p>
        <BanStatistics />
      </main>
      <Footer />
    </div>
  )
}

