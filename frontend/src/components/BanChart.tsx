import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Skeleton } from "@/components/ui/skeleton"
import { BASE_URL } from "@/config/api"
import { format, parseISO } from "date-fns"

interface Ban {
  banId: number
  createdAt: string
  memberId: string
  reason: string
  serverId: number
}

interface ChartData {
  date: string
  count: number
}

export const BanChart = () => {
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${BASE_URL}/api/bans`, {
          credentials: "include",
        })
        if (!response.ok) {
          throw new Error("Failed to fetch ban data")
        }
        const data = await response.json()
        const bans: Ban[] = data.bans

        // Create a map to store ban counts by date
        const banCountsByDate = new Map<string, number>()

        // Process each ban and count by formatted date
        bans.forEach((ban) => {
          // Parse the ISO string and format it consistently
          const date = format(parseISO(ban.createdAt), 'dd/MM/yyyy')
          banCountsByDate.set(date, (banCountsByDate.get(date) || 0) + 1)
        })

        // Convert the map to array and sort by date
        const formattedData: ChartData[] = Array.from(banCountsByDate.entries())
          .map(([date, count]) => ({
            date: format(parseISO(date.split('/').reverse().join('-')), 'dd/MM'),
            count,
            // Keep original date for sorting
            originalDate: parseISO(date.split('/').reverse().join('-'))
          }))
          .sort((a, b) => (a.originalDate as Date).getTime() - (b.originalDate as Date).getTime())
          .map(({ date, count }) => ({ date, count }))

        setChartData(formattedData)
      } catch (err) {
        console.error('Error fetching ban data:', err)
        setError("Failed to load ban data")
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

  if (error) {
    return (
      <Card className="w-full h-[300px] flex items-center justify-center">
        <CardContent>{error}</CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Bans per Day</CardTitle>
        <CardDescription>Number of bans issued each day</CardDescription>
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
              <XAxis 
                dataKey="date" 
                tickLine={false} 
                axisLine={false} 
                tick={{ fontSize: 12 }}
              />
              <YAxis
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => Math.round(value).toString()}
                interval={0}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Bar 
                dataKey="count" 
                fill="hsl(var(--primary))" 
                radius={[4, 4, 0, 0]} 
                maxBarSize={50} 
              />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

