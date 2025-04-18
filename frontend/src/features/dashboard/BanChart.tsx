import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Skeleton } from "@/components/ui/skeleton"
import { BASE_URL } from "@/config/api"
import { parseISO, subDays, subMonths, isAfter } from "date-fns"
import { formatInTimeZone } from "date-fns-tz"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

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
  originalDate?: Date
}

type TimeRange = '7days' | '30days' | '3months' | '6months' | 'all'

export const BanChart = () => {
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [allBansData, setAllBansData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [timeRange, setTimeRange] = useState<TimeRange>('30days')

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

        // Process each ban and count by formatted date in UTC
        bans.forEach((ban) => {
          try {
            if (!ban.createdAt) {
              console.warn("Ban missing createdAt:", ban)
              return
            }
            
            // Parse the ISO date string
            const parsedDate = parseISO(ban.createdAt)
            // Format in UTC
            const formattedDate = formatInTimeZone(parsedDate, 'UTC', 'dd/MM/yyyy')
            
            banCountsByDate.set(formattedDate, (banCountsByDate.get(formattedDate) || 0) + 1)
          } catch (err) {
            console.error("Error processing ban date:", ban.createdAt, err)
          }
        })

        // Convert the map to array and sort by date
        const formattedData: ChartData[] = Array.from(banCountsByDate.entries())
          .map(([date, count]) => {
            try {
              return {
                date: date.slice(0, 5), // Just take dd/MM part
                count,
                originalDate: parseISO(date.split('/').reverse().join('-'))
              }
            } catch (err) {
              console.error("Error formatting date:", date, err)
              return null
            }
          })
          .filter((item): item is NonNullable<typeof item> => item !== null)
          .sort((a, b) => a.originalDate!.getTime() - b.originalDate!.getTime())

        // Store the full data set
        setAllBansData(formattedData)
        
        // Apply the initial time filter
        filterDataByTimeRange(formattedData, timeRange)
      } catch (err) {
        console.error('Error fetching ban data:', err)
        setError("Failed to load ban data")
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  useEffect(() => {
    // Apply time range filter whenever it changes
    filterDataByTimeRange(allBansData, timeRange)
  }, [timeRange, allBansData])

  const filterDataByTimeRange = (data: ChartData[], range: TimeRange) => {
    if (!data.length) return

    const now = new Date()
    let cutoffDate: Date

    switch (range) {
      case '7days':
        cutoffDate = subDays(now, 7)
        break
      case '30days':
        cutoffDate = subDays(now, 30)
        break
      case '3months':
        cutoffDate = subMonths(now, 3)
        break
      case '6months':
        cutoffDate = subMonths(now, 6)
        break
      case 'all':
      default:
        // No filtering needed for "all"
        setChartData(data.map(({ date, count }) => ({ date, count })))
        return
    }

    // Filter data to include only dates after the cutoff
    const filteredData = data
      .filter(item => item.originalDate && isAfter(item.originalDate, cutoffDate))
      .map(({ date, count }) => ({ date, count }))

    setChartData(filteredData)
  }

  const handleTimeRangeChange = (value: string) => {
    setTimeRange(value as TimeRange)
  }

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
    <Card className="w-full h-[600px]">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle>Bans per Day</CardTitle>
          <CardDescription>Number of bans issued each day</CardDescription>
        </div>
        <div className="flex items-center">
          <span className="text-sm text-muted-foreground mr-2">Time range:</span>
          <Select value={timeRange} onValueChange={handleTimeRangeChange}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Select range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7days">Last 7 days</SelectItem>
              <SelectItem value="30days">Last 30 days</SelectItem>
              <SelectItem value="3months">Last 3 months</SelectItem>
              <SelectItem value="6months">Last 6 months</SelectItem>
              <SelectItem value="all">All time</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent className="flex-1">
        <ChartContainer
          config={{
            count: {
              label: "Bans",
              color: "hsl(var(--primary))",
            },
          }}
          className="h-full"
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