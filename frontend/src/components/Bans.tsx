import { useEffect, useState, useCallback } from "react"
import { Header } from "./Header"
import { Footer } from "./Footer"
import { useAuth } from "@/contexts/AuthContext"
import { useToast } from "@/hooks/use-toast"
import { BASE_URL } from "@/config/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { AdminActions } from "./AdminActions"
import { DataTable } from "./DataTable"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "./ui/dialog"
import { Label } from "./ui/label"
import { Input } from "./ui/input"
import { Button } from "./ui/button"

interface Ban {
  banId: number
  capturedMessage: string
  createdAt: string
  memberId: string
  reason: string
  serverId: string
}



export function Bans() {
  const [bans, setBans] = useState<Ban[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const { toast } = useToast()
  const { user } = useAuth()

  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [editingBanId, setEditingBanId] = useState<number | null>(null)
  const [editReason, setEditReason] = useState("")
  const [editCapturedMessage, setEditCapturedMessage] = useState("")

  const fetchBans = async () => {
    try {
      const response = await fetch(`${BASE_URL}/api/bans`, {
        credentials: "include",
      })
      if (!response.ok) {
        throw new Error("Failed to fetch ban data")
      }
      const data = await response.json()
      setBans(data.bans)
    } catch (err) {
      setError("Failed to load ban data")
      toast({
        title: "Error",
        description: "Failed to load ban data",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchBans()
  }, [])

  const filteredBans = bans.filter(
    (ban) =>
      ban.capturedMessage.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ban.reason.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ban.memberId.includes(searchTerm)
  )

  const handleEdit = useCallback(
    async (banId: number) => {
      try {
        const response = await fetch(`${BASE_URL}/api/ban/${banId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ reason: editReason, capturedMessage: editCapturedMessage }),
          credentials: "include",
        })

        if (!response.ok) {
          throw new Error("Failed to update ban")
        }

        const data = await response.json()
        toast({
          title: "Ban Updated",
          description: data.message,
        })
        setIsEditDialogOpen(false)
        fetchBans() // Refresh the ban list
      } catch (error) {
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "An error occurred while updating the ban",
          variant: "destructive",
        })
      }
    },
    [editReason, editCapturedMessage, toast, fetchBans]
  )

  const handleDelete = useCallback(
    async (banId: number) => {
      try {
        const response = await fetch(`${BASE_URL}/api/ban/${banId}`, {
          method: "DELETE",
          credentials: "include",
        })

        if (!response.ok) {
          throw new Error("Failed to delete ban")
        }

        const data = await response.json()
        toast({
          title: "Ban Deleted",
          description: data.message,
        })
        fetchBans() // Refresh the ban list
      } catch (error) {
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "An error occurred while deleting the ban",
          variant: "destructive",
        })
      }
    },
    [toast, fetchBans]
  )

  const handleEditClick = (banId: number, reason: string, capturedMessage: string) => {
    setEditingBanId(banId)
    setEditReason(reason)
    setEditCapturedMessage(capturedMessage)
    setIsEditDialogOpen(true)
  }

  if (loading) {
    return <div>Loading bans...</div>
  }

  if (error) {
    return <div>{error}</div>
  }


  return (
    <>
      <div className="flex flex-col min-h-screen">
        <Header />
  //    <main className="flex-grow container mx-auto px-4 py-8 max-w-4xl">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Moderator Actions</CardTitle>
              <CardDescription>Recent moderation activities including bans</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between items-center mb-4">
                <Input
                  placeholder="Search by message, reason, or member ID..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-sm"
                />
                {user?.is_admin && <AdminActions onBanAdded={fetchBans} />}
              </div>
              <DataTable
                bans={filteredBans}
                onEdit={handleEditClick}
                onDelete={handleDelete}
                isAdmin={user?.is_admin || false}
              />
            </CardContent>
          </Card>
          <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Edit Ban</DialogTitle>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="reason" className="text-right">
                    Reason
                  </Label>
                  <Input
                    id="reason"
                    value={editReason}
                    onChange={(e) => setEditReason(e.target.value)}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="capturedMessage" className="text-right">
                    Captured Message
                  </Label>
                  <Input
                    id="capturedMessage"
                    value={editCapturedMessage}
                    onChange={(e) => setEditCapturedMessage(e.target.value)}
                    className="col-span-3"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" onClick={() => editingBanId && handleEdit(editingBanId)}>
                  Save changes
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
      </main>
      <Footer />
      </div>
    </>


  )
}

