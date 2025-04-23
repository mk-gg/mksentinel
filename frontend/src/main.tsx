import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { PusherProvider } from './contexts/PusherContext'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <PusherProvider>
      <App />
    </PusherProvider>
  </React.StrictMode>,
)