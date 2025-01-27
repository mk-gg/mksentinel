import { Card, CardContent, CardHeader, CardTitle} from "./ui/card"

export function BanStatistics() {

    return (
        <div className="grid gap-4 md:grid-cols-3">
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Bans</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{1}</div>
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Bans Today</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{10}</div>
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Placeholder</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">-</div>
                </CardContent>
            </Card>
        </div>
    )
}