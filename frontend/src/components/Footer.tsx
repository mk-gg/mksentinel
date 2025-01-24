import type React from "react"

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-100 mt-auto">
      <div className="container mx-auto px-4 py-6 text-center text-gray-600">
        <p>&copy; {new Date().getFullYear()} YourAppName. All rights reserved.</p>
      </div>
    </footer>
  )
}

export default Footer

