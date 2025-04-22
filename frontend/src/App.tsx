import { BrowserRouter as Router, Route, Routes, Navigate, useLocation } from "react-router-dom"
import { LoginPage } from "./features/login/LoginPage"
import { HomePage } from "./pages/HomePage"
import { Bans } from "./features/bans/Bans"
import { AuthProvider, useAuth } from "./contexts/AuthContext"
import { useEffect } from "react"
import { BanRepository } from "./repositories/banRepository"

// Component to handle prefetching based on current route
function PrefetchRouteData() {
  const location = useLocation()
  const { user } = useAuth()
  
  useEffect(() => {
    // Only prefetch data if user is authenticated
    if (!user) return
    
    const banRepository = BanRepository.getInstance()

    // Prefetch data based on current path or upcoming paths
    const prefetchData = async () => {
      // When on home page, prefetch bans data for the Bans page
      if (location.pathname === '/') {
        console.log('Prefetching bans data for potential navigation to Bans page')
        await banRepository.getBans(false)
      }
      
      // When on bans page and first load, no need to prefetch home data since it's smaller
      // and likely already loaded in the initial prefetch
    }

    prefetchData()
  }, [location.pathname, user])
  
  return null // This component doesn't render anything
}

// Component to prefetch common data on initial app load
function InitialDataPrefetcher() {
  const { user } = useAuth()
  
  useEffect(() => {
    // Only prefetch data if user is authenticated
    if (!user) return
    
    const prefetchInitialData = async () => {
      console.log('Prefetching initial app data')
      const banRepository = BanRepository.getInstance()
      
      // Prefetch essential data that's common across pages
      await Promise.all([
        banRepository.getBanStatistics(),
        banRepository.getBans()
      ])
    }
    
    prefetchInitialData()
  }, [user]) // Re-run if user auth status changes
  
  return null // This component doesn't render anything
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <InitialDataPrefetcher />
        <PrefetchRouteData />
        <AppRoutes />
      </Router>
    </AuthProvider>
  )
}

function AppRoutes() {
  const { user, loading } = useAuth()

  if (loading) {
    return null // Return nothing during initial auth check
  }

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" /> : <LoginPage />} />
      <Route path="/" element={user ? <HomePage /> : <Navigate to="/login" />} />
      <Route path="/bans" element={user ? <Bans /> : <Navigate to="/login" />} />
    </Routes>
  )
}

export default App