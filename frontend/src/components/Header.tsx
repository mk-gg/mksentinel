import { useState } from "react"
import { Link } from "react-router-dom"
import { Button } from "./ui/button"
import { Avatar, AvatarFallback } from "./ui/avatar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu"

interface User {
  username: string
  email: string
}

interface HeaderProps {
  user: User
  onLogout: () => void
  onNavigate: (path: string) => void
}

export function Header({ user, onLogout, onNavigate}: HeaderProps) {
  const [isOpen, setIsOpen] = useState(false)

  const initials = user.username
    .split(" ")
    .map((name) => name[0])
    .join("")
    .toUpperCase()

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <Link to="/" className="font-bold text-xl hover:text-primary transition-colors">
          Sentinel
        </Link>
        <nav className="flex items-center space-x-4">
          <Button variant="ghost" onClick={() => onNavigate("/")}>
            Home
          </Button>
          <Button variant="ghost" onClick={() => onNavigate("/bans")}>
            Bans
          </Button>
          <Button variant="ghost">Contact</Button>
          <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
            <DropdownMenuTrigger asChild>
              <Avatar className="cursor-pointer">
                <AvatarFallback>{initials}</AvatarFallback>
              </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={onLogout}>Logout</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </nav>
      </div>
    </header>
  )
}

