import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'

export function LoginPage() {
  const { login } = useAuth()

  return (
    <div className="flex items-center justify-center min-h-screen bg-background px-4">
      <div className="w-full max-w-md p-8 space-y-6 bg-card rounded-lg border shadow-lg">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold">Login</h1>
          <p className="text-muted-foreground">Sign in to continue to MK Sentinel</p>
        </div>
        <div className="space-y-4">
          <Button 
            onClick={login} 
            className="w-full flex items-center justify-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <path d="M8 12h8" />
              <path d="M12 8v8" />
            </svg>
            Sign in with Google
          </Button>
        </div>
      </div>
    </div>
  )
} 