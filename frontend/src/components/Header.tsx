import { useState } from "react"
import { Link } from "react-router-dom"
import { Button } from "./ui/button"
import { Avatar, AvatarFallback } from "./ui/avatar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu"
import { useAuth } from "../contexts/AuthContext"
import { Skeleton } from "@/components/ui/skeleton"

export function Header() {
  const [isOpen, setIsOpen] = useState(false)
  const { user, logout, loading } = useAuth()

  if (loading) {
    return (
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <Skeleton className="h-8 w-[100px]" />
          <div className="flex items-center space-x-4">
            <Skeleton className="h-10 w-[60px]" />
            <Skeleton className="h-10 w-[60px]" />
            <Skeleton className="h-10 w-[60px]" />
            <Skeleton className="h-10 w-10 rounded-full" />
          </div>
        </div>
      </header>
    )
  }

  if (!user) {
    return null // Don't render the header if there's no user
  }

  const initials = user.username
    .split(" ")
    .map((name) => name[0])
    .join("")
    .toUpperCase()

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <Link to="/" className="font-bold text-xl hover:text-primary transition-colors">
          Sentinel
        </Link>
        <nav className="flex items-center space-x-4">
          <Button variant="ghost" asChild>
            <Link to="/">Home</Link>
          </Button>
          <Button variant="ghost" asChild>
            <Link to="/bans">Bans</Link>
          </Button>
          <Button variant="ghost">Contact</Button>
          <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
            <DropdownMenuTrigger asChild>
              <Avatar className="cursor-pointer">
                <AvatarFallback>{initials}</AvatarFallback>
              </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={logout}>Logout</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </nav>
      </div>
    </header>
  )
}

