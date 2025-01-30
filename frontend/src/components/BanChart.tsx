import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Skeleton } from "@/components/ui/skeleton"
import { BASE_URL } from "@/config/api"

interface MonthlyTrend {
  month: string
  count: number
}

interface BanStatistics {
  totalBans: number
  totalBansToday: number
  totalBansMonth: number
  totalBansYear: number
  totalServers: number
  totalMembers: number
  monthlyTrend: MonthlyTrend[]
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString("default", { month: "short", year: "numeric" })
}

export const BanChart = () => {
  const [statistics, setStatistics] = useState<BanStatistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${BASE_URL}/api/bans/statistics`, {
          credentials: "include",
        })
        if (!response.ok) {
          throw new Error("Failed to fetch ban statistics")
        }
        const data: BanStatistics = await response.json()
        setStatistics(data)
      } catch (err) {
        setError("Failed to load ban statistics")
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <Skeleton className="h-8 w-[200px]" />
          <Skeleton className="h-4 w-[300px]" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[200px] w-full" />
        </CardContent>
      </Card>
    )
  }

  if (error || !statistics) {
    return (
      <Card className="w-full h-[300px] flex items-center justify-center">
        <CardContent>{error || "No data available"}</CardContent>
      </Card>
    )
  }

  const chartData = statistics.monthlyTrend.map((item) => ({
    ...item,
    month: formatDate(item.month),
  }))

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Monthly Ban Trend</CardTitle>
        <CardDescription>Number of bans issued each month</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            count: {
              label: "Bans",
              color: "hsl(var(--primary))",
            },
          }}
          className="h-[200px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fontSize: 12 }} />
              <YAxis
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => Math.round(value).toString()}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} maxBarSize={50} />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

