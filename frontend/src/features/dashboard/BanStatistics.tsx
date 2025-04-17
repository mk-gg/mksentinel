import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card"
import { BASE_URL } from '@/config/api'
import { Skeleton } from '@/components/ui/skeleton'

interface BanStats {
    totalBans: number
    totalBansToday: number
    totalBansMonth: number
}


export function BanStatistics() {
    const [stats, setStats] = useState<BanStats>({ totalBans: 0, totalBansToday: 0, totalBansMonth: 0 })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchStats = async () => {
          try {
            const response = await fetch(`${BASE_URL}/api/bans/statistics`, {
              credentials: 'include'
            })
            if (!response.ok) {
              throw new Error('Failed to fetch ban statistics')
            }
            const data = await response.json()
            setStats(data)
          } catch (error) {
            console.error('Error fetching ban statistics:', error)
          } finally {
            setLoading(false)
          }
        }
    
        fetchStats()
      }, [])

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

    return (
        <div className="grid gap-4 md:grid-cols-3">
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Bans</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{stats.totalBans}</div>
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Bans Today</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{stats.totalBansToday}</div>
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Monthly Bans</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{stats.totalBansMonth}</div>
                </CardContent>
            </Card>
        </div>
    )
} 