import { Header } from "./Header"
import { Footer } from "./Footer"
import { BanStatistics } from "./BanStatistics"
import { BanChart } from "./BanChart"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/contexts/AuthContext"

export function HomePage() {
  const { loading } = useAuth()

  if (loading) {
    return (
      <div className="flex flex-col min-h-screen">
        <Header />
        <main className="flex-grow container mx-auto px-4 py-8 max-w-4xl">
          <Skeleton className="h-8 w-[300px] mb-4" />
          <Skeleton className="h-4 w-[500px] mb-8" />
          <div className="space-y-8">
            <BanStatistics />
            <BanChart />
          </div>
        </main>
        <Footer />
      </div>
    )
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-8">
          <BanStatistics />
          <BanChart />
        </div>
      </main>
      <Footer />
    </div>
  )
}

