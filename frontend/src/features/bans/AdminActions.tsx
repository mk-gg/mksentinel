import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
import { useBanRepository } from "@/hooks/useBanRepository"

interface NewBan {
  memberId: string
  username: string
  displayName: string
  serverId: string
  serverName: string
  capturedMessage: string
  reason: string
}

interface AdminActionsProps {
  onBanAdded: () => void
}

export const AdminActions: React.FC<AdminActionsProps> = ({ onBanAdded }) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [newBan, setNewBan] = useState<NewBan>({
    memberId: '',
    username: '',
    displayName: '',
    serverId: '',
    serverName: '',
    capturedMessage: '',
    reason: ''
  })
  const { toast } = useToast()
  const { createBan } = useBanRepository()

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setNewBan(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await createBan(newBan)

      if (!response.error) {
        toast({
          title: "Ban Added",
          description: `Successfully banned user ${newBan.username}`,
        })
        setIsDialogOpen(false)
        onBanAdded()
      } else {
        throw new Error(response.error)
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'An error occurred while adding the ban',
        variant: "destructive",
      })
    }
  }

  return (
    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <DialogTrigger asChild>
        <Button>Add New Ban</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add New Ban</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="memberId">Member ID</Label>
              <Input id="memberId" name="memberId" value={newBan.memberId} onChange={handleInputChange} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input id="username" name="username" value={newBan.username} onChange={handleInputChange} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="displayName">Display Name</Label>
              <Input id="displayName" name="displayName" value={newBan.displayName} onChange={handleInputChange} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="serverId">Server ID</Label>
              <Input id="serverId" name="serverId" value={newBan.serverId} onChange={handleInputChange} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="serverName">Server Name</Label>
              <Input id="serverName" name="serverName" value={newBan.serverName} onChange={handleInputChange} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="reason">Reason</Label>
              <Input id="reason" name="reason" value={newBan.reason} onChange={handleInputChange} required />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="capturedMessage">Captured Message</Label>
            <Input id="capturedMessage" name="capturedMessage" value={newBan.capturedMessage} onChange={handleInputChange} />
          </div>
          <Button type="submit">Add Ban</Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}