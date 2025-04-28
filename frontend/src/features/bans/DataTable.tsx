import { useState, useEffect, useRef } from 'react'
import { parseISO } from 'date-fns'
import { formatInTimeZone } from 'date-fns-tz'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, MoreHorizontal } from 'lucide-react'
import { Card, CardContent } from "@/components/ui/card"
import { motion } from 'framer-motion'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import {
  Dialog,
  DialogContent,
  DialogDescription as DialogDesc,
  DialogHeader as DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface Ban {
  banId: number
  capturedMessage: string
  createdAt: string
  memberId: string
  reason: string
  serverId: string
}

interface DataTableProps {
  bans: Ban[]
  onEdit: (banId: number, reason: string, capturedMessage: string) => void
  onDelete: (banId: number) => void
  isAdmin: boolean
}

const ROWS_PER_PAGE_OPTIONS = [10, 20, 50, 100]

export function DataTable({ bans, onEdit, onDelete, isAdmin }: DataTableProps) {
  const [currentPage, setCurrentPage] = useState(1)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [newOrUpdatedBans, setNewOrUpdatedBans] = useState<Record<number, boolean>>({})
  const previousBans = useRef<Ban[]>([]);

  const formatDate = (dateString: string) => {
    try {
      const parsedDate = parseISO(dateString)
      return formatInTimeZone(parsedDate, 'UTC', 'dd/MM/yyyy HH:mm:ss')
    } catch (error) {
      console.error('Error formatting date:', error)
      return dateString
    }
  }

  // Track changes to highlight newly added or updated bans
  useEffect(() => {
    if (previousBans.current.length > 0) {
      const updatedIds: Record<number, boolean> = {};
      
      // Check for new or updated bans
      bans.forEach(ban => {
        const prevBan = previousBans.current.find(b => b.banId === ban.banId);
        
        // New ban
        if (!prevBan) {
          updatedIds[ban.banId] = true;
        } 
        // Updated ban (reason or message changed)
        else if (
          prevBan.reason !== ban.reason || 
          prevBan.capturedMessage !== ban.capturedMessage
        ) {
          updatedIds[ban.banId] = true;
        }
      });
      
      if (Object.keys(updatedIds).length > 0) {
        setNewOrUpdatedBans(updatedIds);
        
        // Clear highlight after 3 seconds
        const timer = setTimeout(() => {
          setNewOrUpdatedBans({});
        }, 3000);
        
        return () => clearTimeout(timer);
      }
    }
    
    // Update reference for next comparison
    previousBans.current = [...bans];
  }, [bans]);

  const totalPages = Math.ceil(bans.length / rowsPerPage)
  const paginatedBans = bans.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage)

  const handlePageChange = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)))
  }

  const handleRowsPerPageChange = (value: string) => {
    setRowsPerPage(Number(value))
    setCurrentPage(1)
  }

  // Determine if a row should be highlighted
  const isHighlighted = (banId: number) => {
    return newOrUpdatedBans[banId] || false;
  }

  // Dropdown menu for actions
  const ActionMenu = ({ ban }: { ban: Ban }) => (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="h-8 w-8 p-0">
          <span className="sr-only">Open menu</span>
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[160px]">
        <DropdownMenuItem onSelect={(event) => event.preventDefault()}>
          <Dialog>
            <DialogTrigger className="w-full text-left">View Details</DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Ban Details</DialogTitle>
                <DialogDesc>
                  Full details of the selected ban.
                </DialogDesc>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div>
                  <p><strong>Date:</strong> {formatDate(ban.createdAt)}</p>
                  <p><strong>Reason:</strong> {ban.reason}</p>
                  <p><strong>Captured Message:</strong> {ban.capturedMessage}</p>
                  <p><strong>Member ID:</strong> {ban.memberId}</p>
                  <p><strong>Server ID:</strong> {ban.serverId}</p>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </DropdownMenuItem>
        <DropdownMenuItem onSelect={() => onEdit(ban.banId, ban.reason, ban.capturedMessage)} className="px-2 py-1.5">
          Edit
        </DropdownMenuItem>
        <DropdownMenuItem onSelect={(event) => event.preventDefault()} className="text-red-600 focus:bg-red-100 focus:text-red-600">
          <AlertDialog>
            <AlertDialogTrigger className="w-full text-left">Delete</AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone. This will permanently delete the ban
                  record and remove it from our servers.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={() => onDelete(ban.banId)}>
                  Delete
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )

  // Mobile card view
  const MobileView = () => (
    <div className="space-y-4">
      {paginatedBans.map((ban) => (
        isHighlighted(ban.banId) ? (
          <motion.div 
            key={ban.banId}
            initial={{ backgroundColor: "rgba(74, 222, 128, 0.2)" }}
            animate={{ backgroundColor: "rgba(74, 222, 128, 0)" }}
            transition={{ duration: 3 }}
          >
            <Card className="overflow-hidden">
              <CardContent className="p-4">
                <div className="grid grid-cols-1 gap-2">
                  <div className="flex justify-between items-center">
                    <div className="font-medium text-sm">{formatDate(ban.createdAt)}</div>
                    {isAdmin && <ActionMenu ban={ban} />}
                  </div>
                  <div className="pt-2">
                    <div className="font-semibold text-sm">Reason</div>
                    <div className="text-sm truncate">{ban.reason}</div>
                  </div>
                  <div>
                    <div className="font-semibold text-sm">Message</div>
                    <div className="text-sm truncate max-w-full">{ban.capturedMessage}</div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 pt-1">
                    <div>
                      <div className="font-semibold text-xs">Member ID</div>
                      <div className="text-xs truncate">{ban.memberId}</div>
                    </div>
                    <div>
                      <div className="font-semibold text-xs">Server ID</div>
                      <div className="text-xs truncate">{ban.serverId}</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          <Card key={ban.banId} className="overflow-hidden">
            <CardContent className="p-4">
              <div className="grid grid-cols-1 gap-2">
                <div className="flex justify-between items-center">
                  <div className="font-medium text-sm">{formatDate(ban.createdAt)}</div>
                  {isAdmin && <ActionMenu ban={ban} />}
                </div>
                <div className="pt-2">
                  <div className="font-semibold text-sm">Reason</div>
                  <div className="text-sm truncate">{ban.reason}</div>
                </div>
                <div>
                  <div className="font-semibold text-sm">Message</div>
                  <div className="text-sm truncate max-w-full">{ban.capturedMessage}</div>
                </div>
                <div className="grid grid-cols-2 gap-2 pt-1">
                  <div>
                    <div className="font-semibold text-xs">Member ID</div>
                    <div className="text-xs truncate">{ban.memberId}</div>
                  </div>
                  <div>
                    <div className="font-semibold text-xs">Server ID</div>
                    <div className="text-xs truncate">{ban.serverId}</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )
      ))}
    </div>
  )

  // Desktop table view
  const DesktopView = () => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Date</TableHead>
          <TableHead>Reason</TableHead>
          <TableHead>Captured Message</TableHead>
          <TableHead>Member ID</TableHead>
          <TableHead>Server ID</TableHead>
          {isAdmin && <TableHead className="w-[100px]" />}
        </TableRow>
      </TableHeader>
      <TableBody>
        {paginatedBans.map((ban) => (
          isHighlighted(ban.banId) ? (
            <motion.tr
              key={ban.banId}
              className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted"
              initial={{ backgroundColor: "rgba(74, 222, 128, 0.2)" }}
              animate={{ backgroundColor: "rgba(74, 222, 128, 0)" }}
              transition={{ duration: 3 }}
            >
              <TableCell>{formatDate(ban.createdAt)}</TableCell>
              <TableCell>{ban.reason}</TableCell>
              <TableCell className="max-w-xs truncate">{ban.capturedMessage}</TableCell>
              <TableCell>{ban.memberId}</TableCell>
              <TableCell>{ban.serverId}</TableCell>
              {isAdmin && (
                <TableCell className="text-center">
                  <ActionMenu ban={ban} />
                </TableCell>
              )}
            </motion.tr>
          ) : (
            <TableRow key={ban.banId}>
              <TableCell>{formatDate(ban.createdAt)}</TableCell>
              <TableCell>{ban.reason}</TableCell>
              <TableCell className="max-w-xs truncate">{ban.capturedMessage}</TableCell>
              <TableCell>{ban.memberId}</TableCell>
              <TableCell>{ban.serverId}</TableCell>
              {isAdmin && (
                <TableCell className="text-center">
                  <ActionMenu ban={ban} />
                </TableCell>
              )}
            </TableRow>
          )
        ))}
      </TableBody>
    </Table>
  )

  return (
    <>
      {/* Mobile view for small screens, desktop view for medium screens and up */}
      <div className="md:hidden">
        <MobileView />
      </div>
      <div className="hidden md:block">
        <DesktopView />
      </div>

      {/* Pagination controls - same for both views */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0 py-4">
        <div className="text-sm text-muted-foreground">
          {paginatedBans.length} of {bans.length} row(s) selected.
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center space-y-3 sm:space-y-0 sm:space-x-6 lg:space-x-8">
          <div className="flex items-center space-x-2">
            <p className="text-sm font-medium">Rows</p>
            <Select
              value={rowsPerPage.toString()}
              onValueChange={handleRowsPerPageChange}
            >
              <SelectTrigger className="h-8 w-[70px]">
                <SelectValue placeholder={rowsPerPage} />
              </SelectTrigger>
              <SelectContent side="top">
                {ROWS_PER_PAGE_OPTIONS.map((option) => (
                  <SelectItem key={option} value={option.toString()}>
                    {option}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center justify-center text-sm font-medium">
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              className="hidden h-8 w-8 p-0 lg:flex"
              onClick={() => handlePageChange(1)}
              disabled={currentPage === 1}
            >
              <span className="sr-only">Go to first page</span>
              <ChevronsLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              className="h-8 w-8 p-0"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              <span className="sr-only">Go to previous page</span>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              className="h-8 w-8 p-0"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              <span className="sr-only">Go to next page</span>
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              className="hidden h-8 w-8 p-0 lg:flex"
              onClick={() => handlePageChange(totalPages)}
              disabled={currentPage === totalPages}
            >
              <span className="sr-only">Go to last page</span>
              <ChevronsRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </>
  )
}