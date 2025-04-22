import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Skeleton } from "@/components/ui/skeleton"
import { parseISO, subDays, subMonths, isAfter } from "date-fns"
import { formatInTimeZone } from "date-fns-tz"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useBanRepository } from "@/hooks/useBanRepository"
import { Button } from "@/components/ui/button"

// att
interface ChartData {
  date: string
  count: number
  originalDate?: Date
}

type TimeRange = '7days' | '30days' | '3months' | '6months' | 'all'

export const BanChart = () => {
  const { bans, loading, error, fetchBans } = useBanRepository()
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [allBansData, setAllBansData] = useState<ChartData[]>([])
  const [timeRange, setTimeRange] = useState<TimeRange>('30days')

  // Process bans data when it changes
  useEffect(() => {
    if (!loading && bans.length > 0) {
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
      
      // Apply the time filter
      filterDataByTimeRange(formattedData, timeRange)
    }
  }, [bans, loading, timeRange])

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
      <Card className="w-full">
        <CardContent className="py-8">
          <div className="text-red-500 text-center">Error loading ban data: {error}</div>
          <div className="flex justify-center mt-4">
            <Button onClick={() => fetchBans(true)}>Retry</Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-2 sm:space-y-0 pb-4">
        <div>
          <CardTitle>Bans Trend</CardTitle>
          <CardDescription>Ban activity over time</CardDescription>
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
      <CardContent>
        <div className="w-full h-[300px] sm:h-[350px] md:h-[400px]">
          <ChartContainer
            config={{
              count: {
                label: "Bans",
                color: "hsl(var(--chart-primary))",
              },
            }}
            className="w-full h-full"
          >
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart 
                data={chartData} 
                margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
              >
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--chart-primary))" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="hsl(var(--chart-primary))" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <XAxis 
                  dataKey="date" 
                  tickLine={false} 
                  axisLine={false} 
                  tick={{ fontSize: 12, dy: 10 }}
                  interval="preserveStartEnd"
                  minTickGap={10}
                />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => Math.round(value).toString()}
                  width={40}
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Area 
                  type="monotone" 
                  dataKey="count" 
                  stroke="hsl(var(--chart-primary))" 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#colorCount)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartContainer>
        </div>
      </CardContent>
    </Card>
  )
}