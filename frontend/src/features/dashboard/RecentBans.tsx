import { useEffect, useState } from 'react';
import { usePusher } from '@/contexts/PusherContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatDistanceToNow } from 'date-fns';
import { motion, AnimatePresence } from 'framer-motion';

interface Ban {
  id: number;
  user_id: string;
  reason: string;
  created_at: string;
  // Add other relevant ban fields
}

export function RecentBans() {
  const { recentBans, addBanListener } = usePusher();
  const [bans, setBans] = useState<Ban[]>([]);
  
  // Initial data fetch
  useEffect(() => {
    const fetchRecentBans = async () => {
      try {
        const response = await fetch('/api/recent-bans');
        if (response.ok) {
          const data = await response.json();
          setBans(data);
        }
      } catch (error) {
        console.error('Error fetching recent bans:', error);
      }
    };
    
    fetchRecentBans();
  }, []);
  
  // Update with real-time data from Pusher context
  useEffect(() => {
    if (recentBans.length > 0) {
      setBans(recentBans);
    }
  }, [recentBans]);
  
  // Additional direct event listeners for specific updates
  useEffect(() => {
    // Listen for new bans
    const newBanUnbind = addBanListener('new-ban', (data: { ban: Ban }) => {
      setBans(prev => [data.ban, ...prev].slice(0, 10));
    });
    
    // Listen for ban removals
    const removeBanUnbind = addBanListener('ban-removed', (data: { ban_id: number }) => {
      setBans(prev => prev.filter(ban => ban.id !== data.ban_id));
    });
    
    // Listen for ban updates
    const updateBanUnbind = addBanListener('ban-updated', (data: { ban: Ban }) => {
      setBans(prev => prev.map(ban => ban.id === data.ban.id ? data.ban : ban));
    });
    
    return () => {
      newBanUnbind();
      removeBanUnbind();
      updateBanUnbind();
    };
  }, [addBanListener]);
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Bans</CardTitle>
      </CardHeader>
      <CardContent>
        {bans.length === 0 ? (
          <p className="text-muted-foreground">No recent bans</p>
        ) : (
          <ul className="space-y-4">
            <AnimatePresence>
              {bans.map(ban => (
                <motion.li 
                  key={ban.id} 
                  className="border-b pb-3 last:border-0"
                  initial={{ opacity: 0, backgroundColor: "rgba(0, 255, 0, 0.1)" }}
                  animate={{ opacity: 1, backgroundColor: "rgba(0, 0, 0, 0)" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">{ban.user_id}</p>
                      <p className="text-sm text-muted-foreground">{ban.reason}</p>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(ban.created_at), { addSuffix: true })}
                    </div>
                  </div>
                </motion.li>
              ))}
            </AnimatePresence>
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
