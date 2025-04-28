import { useEffect, useState, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card"
import { Skeleton } from '@/components/ui/skeleton'
import { useBanRepository } from '@/hooks/useBanRepository'
import { motion } from 'framer-motion'

export function BanStatistics() {
    const { banStats, loading, error, fetchBanStatistics } = useBanRepository()
    const [updatedStats, setUpdatedStats] = useState<Record<string, boolean>>({})
    const previousStats = useRef<typeof banStats | null>(null)

    useEffect(() => {
        fetchBanStatistics()
    }, [fetchBanStatistics])

    // Track stats changes for animation effect
    useEffect(() => {
        if (previousStats.current) {
            const updatedFields: Record<string, boolean> = {};
            
            if (previousStats.current.totalBans !== banStats.totalBans) {
                updatedFields.totalBans = true;
            }
            
            if (previousStats.current.totalBansToday !== banStats.totalBansToday) {
                updatedFields.totalBansToday = true;
            }
            
            if (previousStats.current.totalBansMonth !== banStats.totalBansMonth) {
                updatedFields.totalBansMonth = true;
            }
            
            if (Object.keys(updatedFields).length > 0) {
                setUpdatedStats(updatedFields);
                
                // Reset the highlight effect after 2 seconds
                const timer = setTimeout(() => {
                    setUpdatedStats({});
                }, 2000);
                
                return () => clearTimeout(timer);
            }
        }
        
        // Store current stats for next comparison
        previousStats.current = { ...banStats };
    }, [banStats]);

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
                    {updatedStats.totalBans ? (
                        <motion.div 
                            className="text-2xl font-bold"
                            initial={{ backgroundColor: "rgba(74, 222, 128, 0.2)" }}
                            animate={{ backgroundColor: "rgba(74, 222, 128, 0)" }}
                            transition={{ duration: 2 }}
                        >
                            {banStats.totalBans}
                        </motion.div>
                    ) : (
                        <div className="text-2xl font-bold">{banStats.totalBans}</div>
                    )}
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Bans Today</CardTitle>
                </CardHeader>
                <CardContent>
                    {updatedStats.totalBansToday ? (
                        <motion.div 
                            className="text-2xl font-bold"
                            initial={{ backgroundColor: "rgba(74, 222, 128, 0.2)" }}
                            animate={{ backgroundColor: "rgba(74, 222, 128, 0)" }}
                            transition={{ duration: 2 }}
                        >
                            {banStats.totalBansToday}
                        </motion.div>
                    ) : (
                        <div className="text-2xl font-bold">{banStats.totalBansToday}</div>
                    )}
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Monthly Bans</CardTitle>
                </CardHeader>
                <CardContent>
                    {updatedStats.totalBansMonth ? (
                        <motion.div 
                            className="text-2xl font-bold"
                            initial={{ backgroundColor: "rgba(74, 222, 128, 0.2)" }}
                            animate={{ backgroundColor: "rgba(74, 222, 128, 0)" }}
                            transition={{ duration: 2 }}
                        >
                            {banStats.totalBansMonth}
                        </motion.div>
                    ) : (
                        <div className="text-2xl font-bold">{banStats.totalBansMonth}</div>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}