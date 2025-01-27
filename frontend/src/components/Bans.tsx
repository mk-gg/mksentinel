import { Header } from "./Header"
import { Footer } from "./Footer"

export function Bans() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-8 max-w-4xl">
        <h1 className="text-3xl font-bold mb-4">Bans</h1>
        <p className="text-lg">
          This is a placeholder for the Bans page. You can add more content here to describe your application, company,
          or team.
        </p>
      </main>
      <Footer />
    </div>
  )
}

