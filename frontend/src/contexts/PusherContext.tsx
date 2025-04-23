import React, { createContext, useContext, useEffect, useState } from 'react';
import Pusher from 'pusher-js';

// Define environment variables for Pusher
const PUSHER_KEY = import.meta.env.VITE_PUSHER_KEY || 'your-pusher-key';
const PUSHER_CLUSTER = import.meta.env.VITE_PUSHER_CLUSTER || 'us2';

type ConnectionStatus = 'connected' | 'disconnected' | 'connecting';

interface PusherContextType {
  status: ConnectionStatus;
  lastPing: Date | null;
  reconnect: () => void;
}

const PusherContext = createContext<PusherContextType>({
  status: 'disconnected',
  lastPing: null,
  reconnect: () => {},
});

export const usePusher = () => useContext(PusherContext);

export const PusherProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [pusher, setPusher] = useState<Pusher | null>(null);
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [lastPing, setLastPing] = useState<Date | null>(null);

  // Function to initialize Pusher
  const initPusher = () => {
    // Clean up existing connection if any
    if (pusher) {
      pusher.disconnect();
    }

    setStatus('connecting');
    
    // Create new Pusher instance
    const newPusher = new Pusher(PUSHER_KEY, {
      cluster: PUSHER_CLUSTER,
      forceTLS: true,
    });

    // Set up connection event handlers
    newPusher.connection.bind('connected', () => {
      console.log('Pusher connected');
      setStatus('connected');
    });

    newPusher.connection.bind('disconnected', () => {
      console.log('Pusher disconnected');
      setStatus('disconnected');
    });

    newPusher.connection.bind('error', (err: any) => {
      console.error('Pusher connection error:', err);
      setStatus('disconnected');
    });

    // Subscribe to the status channel
    const channel = newPusher.subscribe('sentinel-status');
    
    channel.bind('server-status', (data: any) => {
      console.log('Server status update:', data);
      setLastPing(new Date());
    });

    setPusher(newPusher);
    
    // Ping the server to get initial status
    setTimeout(() => {
      fetch('/api/status').catch(err => console.error('Error pinging server:', err));
    }, 1000);

    return newPusher;
  };

  const reconnect = () => {
    initPusher();
  };

  // Set up ping interval to keep connection status updated
  useEffect(() => {
    const pingServer = () => {
      if (status === 'connected') {
        fetch('/api/status').catch(err => {
          console.error('Error pinging server:', err);
        });
      }
    };

    // Ping the server every 30 seconds to keep connection alive
    const pingInterval = setInterval(pingServer, 30000);

    return () => {
      clearInterval(pingInterval);
    };
  }, [status]);

  // Initialize Pusher connection
  useEffect(() => {
    const newPusher = initPusher();

    // Cleanup on unmount
    return () => {
      if (newPusher) {
        newPusher.disconnect();
      }
    };
  }, []);

  return (
    <PusherContext.Provider value={{ status, lastPing, reconnect }}>
      {children}
    </PusherContext.Provider>
  );
};