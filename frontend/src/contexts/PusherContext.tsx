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

interface Ban {
  id: number;
  user_id: string;
  reason: string;
  created_at: string;
  // Add other relevant ban fields
}

interface PusherContextType {
  status: ConnectionStatus;
  lastPing: Date | null;
  healthStatus: HealthStatus | null;
  reconnect: () => void;
  checkHealth: () => Promise<void>;
  recentBans: Ban[];
  addBanListener: (event: string, callback: (data: any) => void) => () => void;
}

const PusherContext = createContext<PusherContextType>({
  status: 'disconnected',
  lastPing: null,
  healthStatus: null,
  reconnect: () => {},
  checkHealth: async () => {},
  recentBans: [],
  addBanListener: () => () => {},
});

export const usePusher = () => useContext(PusherContext);

export const PusherProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [pusher, setPusher] = useState<Pusher | null>(null);
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [lastPing, setLastPing] = useState<Date | null>(null);
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [recentBans, setRecentBans] = useState<Ban[]>([]);

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

    // Listen for ban updates
    channel.bind('new-ban', (data: { ban: Ban }) => {
      console.log('New ban received:', data);
      setRecentBans(prev => [data.ban, ...prev].slice(0, 10));
    });

    channel.bind('ban-removed', (data: { ban_id: number }) => {
      setRecentBans(prev => prev.filter(ban => ban.id !== data.ban_id));
    });

    channel.bind('ban-updated', (data: { ban: Ban }) => {
      setRecentBans(prev => prev.map(ban => ban.id === data.ban.id ? data.ban : ban));
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

  // Add ban event listener
  const addBanListener = (event: string, callback: (data: any) => void) => {
    if (!pusher) return () => {};
    
    const channel = pusher.channel('sentinel-status') || pusher.subscribe('sentinel-status');
    channel.bind(event, callback);
    
    return () => {
      channel.unbind(event, callback);
    };
  };

  return (
    <PusherContext.Provider value={{ 
      status, 
      lastPing, 
      healthStatus, 
      reconnect, 
      checkHealth,
      recentBans,
      addBanListener
    }}>
      {children}
    </PusherContext.Provider>
  );
};