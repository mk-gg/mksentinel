import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: 
  {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },  
  server: {
    proxy: {
      "/api": "https://mksentinel-backend.vercel.app", // Assuming your Flask server runs on port 5000
    },
  },
})
