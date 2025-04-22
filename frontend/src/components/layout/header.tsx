import { useState } from "react"
import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { useAuth } from "@/contexts/AuthContext"
import { useTheme } from "@/contexts/ThemeContext"
import { Skeleton } from "@/components/ui/skeleton"
import { Moon, Sun } from "lucide-react"

interface HeaderProps {
  showSkeleton?: boolean;
}

export function Header({ showSkeleton = false }: HeaderProps) {
  const [isOpen, setIsOpen] = useState(false)
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()

  if (showSkeleton) {
    return (
      <header className="bg-white shadow-sm">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <Skeleton className="h-8 w-[100px]" />
          <div className="flex items-center space-x-4">
            <Skeleton className="h-10 w-[60px]" />
            <Skeleton className="h-10 w-[60px]" />
            <Skeleton className="h-10 w-10 rounded-full" />
          </div>
        </div>
      </header>
    )
  }

  if (!user) {
    return null
  }

  const initials = user.username
    .split(" ")
    .map((name) => name[0])
    .join("")
    .toUpperCase()

  return (
    <header className="bg-background border-b">
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
          <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
            <DropdownMenuTrigger asChild>
              <Avatar className="cursor-pointer">
                <AvatarFallback>{initials}</AvatarFallback>
              </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={toggleTheme}>
                  {theme === "light" ? (
                    <>
                      <Moon className="mr-2 h-4 w-4" />
                      <span>Dark Mode</span>
                    </>
                  ) : (
                    <>
                      <Sun className="mr-2 h-4 w-4" />
                      <span>Light Mode</span>
                    </>
                  )}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={logout}>Logout</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </nav>
      </div>
    </header>
  )
} 