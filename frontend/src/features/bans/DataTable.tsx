import { useState } from 'react'
import { parseISO } from 'date-fns'
import { formatInTimeZone } from 'date-fns-tz'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, MoreHorizontal } from 'lucide-react'
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

  const formatDate = (dateString: string) => {
    try {
      const parsedDate = parseISO(dateString)
      return formatInTimeZone(parsedDate, 'UTC', 'dd/MM/yyyy HH:mm:ss')
    } catch (error) {
      console.error('Error formatting date:', error)
      return dateString
    }
  }

  const totalPages = Math.ceil(bans.length / rowsPerPage)
  const paginatedBans = bans.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage)

  const handlePageChange = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)))
  }

  const handleRowsPerPageChange = (value: string) => {
    setRowsPerPage(Number(value))
    setCurrentPage(1)
  }

  return (
    <>
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
            <TableRow key={ban.banId}>
              <TableCell>{formatDate(ban.createdAt)}</TableCell>
              <TableCell>{ban.reason}</TableCell>
              <TableCell className="max-w-xs truncate">{ban.capturedMessage}</TableCell>
              <TableCell>{ban.memberId}</TableCell>
              <TableCell>{ban.serverId}</TableCell>
              {isAdmin && (
                <TableCell className="text-center">
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
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <div className="flex items-center justify-between space-x-2 py-4">
        <div className="flex-1 text-sm text-muted-foreground">
          {paginatedBans.length} of {bans.length} row(s) selected.
        </div>
        <div className="flex items-center space-x-6 lg:space-x-8">
          <div className="flex items-center space-x-2">
            <p className="text-sm font-medium">Rows per page</p>
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
          <div className="flex w-[100px] items-center justify-center text-sm font-medium">
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