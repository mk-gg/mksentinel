import { useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card"
import { Skeleton } from '@/components/ui/skeleton'
import { useBanRepository } from '@/hooks/useBanRepository'

export function BanStatistics() {
    const { banStats, loading, error, fetchBanStatistics } = useBanRepository()

    useEffect(() => {
        fetchBanStatistics()
    }, [fetchBanStatistics])

    if (loading) {
        return (
          <div className="grid gap-4 md:grid-cols-3">
            {[...Array(3)].map((_, index) => (
              <Card key={index}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <Skeleton className="h-4 w-[100px]" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-8 w-[60px]" />
                </CardContent>
              </Card>
            ))}
          </div>
        )
    }

    if (error) {
        return (
            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardContent className="py-4">
                        <div className="text-red-500">Error loading statistics: {error}</div>
                    </CardContent>
                </Card>
            </div>
        )
    }

    return (
        <div className="grid gap-4 md:grid-cols-3">
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Bans</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{banStats.totalBans}</div>
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Bans Today</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{banStats.totalBansToday}</div>
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Monthly Bans</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{banStats.totalBansMonth}</div>
                </CardContent>
            </Card>
        </div>
    )
}