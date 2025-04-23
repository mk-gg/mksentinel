import React, { createContext, useContext, useEffect, useState } from 'react';
import Pusher from 'pusher-js';

// Define environment variables for Pusher
const PUSHER_KEY = import.meta.env.VITE_PUSHER_KEY || 'your-pusher-key';
const PUSHER_CLUSTER = import.meta.env.VITE_PUSHER_CLUSTER || 'us2';
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

type ConnectionStatus = 'connected' | 'disconnected' | 'connecting';

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  components: {
    [key: string]: 'connected' | 'disconnected' | 'degraded';
  };
}

interface PusherContextType {
  status: ConnectionStatus;
  lastPing: Date | null;
  healthStatus: HealthStatus | null;
  reconnect: () => void;
  checkHealth: () => Promise<void>;
}

const PusherContext = createContext<PusherContextType>({
  status: 'disconnected',
  lastPing: null,
  healthStatus: null,
  reconnect: () => {},
  checkHealth: async () => {},
});

export const usePusher = () => useContext(PusherContext);

export const PusherProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [pusher, setPusher] = useState<Pusher | null>(null);
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [lastPing, setLastPing] = useState<Date | null>(null);
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);

  // Function to check server health
  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/healthcheck`);
      if (response.ok) {
        const data = await response.json();
        setHealthStatus(data);
        setLastPing(new Date());
        return data;
      }
    } catch (error) {
      console.error('Error checking health:', error);
    }
    return null;
  };

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
      checkHealth();
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
    
    // Listen for server status updates
    channel.bind('server-status', (data: any) => {
      console.log('Server status update:', data);
      setLastPing(new Date());
    });
    
    // Listen for health status updates
    channel.bind('health-update', (data: HealthStatus) => {
      console.log('Health status update:', data);
      setHealthStatus(data);
      setLastPing(new Date());
    });

    setPusher(newPusher);
    
    // Ping the server to get initial status
    setTimeout(() => {
      checkHealth();
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
        checkHealth();
      }
    };

    // Check health every 30 seconds
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
    <PusherContext.Provider value={{ 
      status, 
      lastPing, 
      healthStatus, 
      reconnect, 
      checkHealth 
    }}>
      {children}
    </PusherContext.Provider>
  );
};