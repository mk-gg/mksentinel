import { Header } from "@/components/layout/header"
import { Footer } from "@/components/layout/footer"
import { BanStatistics } from "@/features/dashboard/BanStatistics"
import { BanChart } from "@/features/dashboard/BanChart"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/contexts/AuthContext"

export function HomePage() {
  const { loading } = useAuth()

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Header showSkeleton={loading} />
      <main className="flex-grow container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-8">
          {loading ? (
            <>
              {/* Skeleton for BanStatistics */}
              <div className="grid gap-4 md:grid-cols-3">
                {[...Array(3)].map((_, index) => (
                  <div key={index} className="p-6 rounded-lg border bg-card">
                    <div className="space-y-2">
                      <Skeleton className="h-5 w-24" />
                      <Skeleton className="h-8 w-16" />
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Skeleton for BanChart */}
              <div className="rounded-lg border bg-card">
                <div className="p-6">
                  <div className="space-y-2 mb-4">
                    <Skeleton className="h-6 w-32" />
                    <Skeleton className="h-4 w-48" />
                  </div>
                  <Skeleton className="h-[300px] w-full" />
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