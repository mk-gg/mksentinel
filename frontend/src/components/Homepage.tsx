import { Header } from "./Header"
import { Footer } from "./Footer"
import { BanStatistics } from "./BanStatistics"
import { BanChart } from "./BanChart"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/contexts/AuthContext"

export function HomePage() {
  const { loading } = useAuth()

  return (
    <div className="flex flex-col min-h-screen">
      <Header showSkeleton={loading} />
      <main className="flex-grow container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-8">
          {loading ? (
            <>
              {/* Skeleton for BanStatistics */}
              <div className="grid gap-4 md:grid-cols-3">
                {[...Array(3)].map((_, index) => (
                  <div key={index} className="p-6 rounded-lg border bg-card">
                    <div className="space-y-3">
                      <Skeleton className="h-4 w-[100px]" />
                      <Skeleton className="h-7 w-[60px]" />
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Skeleton for BanChart */}
              <div className="rounded-lg border bg-card">
                <div className="p-6 space-y-4">
                  <div className="space-y-2">
                    <Skeleton className="h-7 w-[140px]" />
                    <Skeleton className="h-4 w-[180px]" />
                  </div>
                  <Skeleton className="h-[400px] w-full" />
                </div>
              </div>
            </>
          ) : (
            <>
              <BanStatistics />
              <BanChart />
            </>
          )}
        </div>
      </main>
      <Footer />
    </div>
  )
}

