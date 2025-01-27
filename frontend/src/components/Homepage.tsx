import { Header } from "./Header"
import { Footer } from "./Footer"
import { BanStatistics } from "./BanStatistics"
import { BanChart } from "./BanChart"

export function HomePage() {

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-8 max-w-4xl">
        <BanStatistics />
        <div></div>
        <BanChart />
      </main>
      <Footer />
    </div>
  )
}

