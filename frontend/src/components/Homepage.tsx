import type React from "react"

const Homepage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Welcome to YourAppName</h1>
      <p className="text-gray-600">
        This is the homepage of your application. You can add more content here as needed.
      </p>
    </div>
  )
}

export default Homepage

