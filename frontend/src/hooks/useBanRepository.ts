import { useState, useEffect, useCallback } from 'react';
import { BanRepository, Ban, BanStatistics } from '@/repositories/banRepository';
import { usePusher } from '@/contexts/PusherContext';

// Define the response type for createBan
interface CreateBanResponse {
  ban?: Ban;
  message?: string;
}

export function useBanRepository() {
  const repository = BanRepository.getInstance();
  const [bans, setBans] = useState<Ban[]>([]);
  const [banStats, setBanStats] = useState<BanStatistics>({ 
    totalBans: 0, 
    totalBansToday: 0, 
    totalBansMonth: 0,
    totalBansYear: 0,
    totalServers: 0,
    totalMembers: 0,
    monthlyTrend: [],
    currentServerTime: new Date().toISOString()
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { addBanListener } = usePusher();

  const fetchBans = useCallback(async (forceRefresh = false) => {
    setLoading(true);
    try {
      const result = await repository.getBans(forceRefresh);
      setBans(result.bans);
      if (result.error) {
        setError(result.error);
      } else {
        setError(null);
      }
    } catch (err) {
      setError('Failed to fetch bans');
      console.error('Error in useBanRepository.fetchBans:', err);
    } finally {
      setLoading(false);
    }
  }, [repository]);

  const fetchBanStatistics = useCallback(async (forceRefresh = false) => {
    setLoading(true);
    try {
      const result = await repository.getBanStatistics(forceRefresh);
      setBanStats(result.stats);
      if (result.error) {
        setError(result.error);
      } else {
        setError(null);
      }
    } catch (err) {
      setError('Failed to fetch ban statistics');
      console.error('Error in useBanRepository.fetchBanStatistics:', err);
    } finally {
      setLoading(false);
    }
  }, [repository]);

  const createBan = useCallback(async (banData: any) => {
    try {
      const result = await repository.createBan(banData);
      
      if (!result.error && result.data) {
        const responseData = result.data as CreateBanResponse;
        
        // If the response includes the created ban
        if (responseData.ban) {
          // Add the new ban to the local state
          setBans(prevBans => [responseData.ban!, ...prevBans]);
          
          // Update statistics
          if (banStats) {
            setBanStats(prevStats => ({
              ...prevStats,
              totalBans: prevStats.totalBans + 1,
              totalBansToday: prevStats.totalBansToday + 1,
              totalBansMonth: prevStats.totalBansMonth + 1
            }));
          }
        }
      }
      
      return result;
    } catch (err) {
      console.error('Error in useBanRepository.createBan:', err);
      throw err;
    }
  }, [repository, banStats]);

  const updateBan = useCallback(async (banId: number, updateData: any) => {
    try {
      // Make the API call to update the ban
      const result = await repository.updateBan(banId, updateData);
      
      if (!result.error) {
        // Update the local state directly instead of refetching all bans
        setBans(prevBans => 
          prevBans.map(ban => 
            ban.banId === banId 
              ? { 
                  ...ban, 
                  ...updateData, 
                  // Ensure we don't lose any fields that weren't updated
                  reason: updateData.reason !== undefined ? updateData.reason : ban.reason,
                  capturedMessage: updateData.capturedMessage !== undefined 
                    ? updateData.capturedMessage 
                    : ban.capturedMessage
                } 
              : ban
          )
        );
      }
      
      return result;
    } catch (err) {
      console.error('Error in useBanRepository.updateBan:', err);
      throw err;
    }
  }, [repository]);

  const deleteBan = useCallback(async (banId: number) => {
    try {
      const result = await repository.deleteBan(banId);
      
      if (!result.error) {
        // Update local state directly by filtering out the deleted ban
        setBans(prevBans => prevBans.filter(ban => ban.banId !== banId));
        
        // Update statistics if needed
        if (banStats) {
          setBanStats(prevStats => ({
            ...prevStats,
            totalBans: Math.max(0, prevStats.totalBans - 1),
            // We can't be sure if the ban was from today or this month, so don't update those
          }));
        }
      }
      
      return result;
    } catch (err) {
      console.error('Error in useBanRepository.deleteBan:', err);
      throw err;
    }
  }, [repository, banStats]);

  // Set up real-time updates via Pusher
  useEffect(() => {
    // Listen for new bans
    const newBanUnbind = addBanListener('new-ban', (data: { ban: Ban }) => {
      setBans(prevBans => {
        // Check if the ban is already in the list
        const exists = prevBans.some(ban => ban.banId === data.ban.banId);
        if (!exists) {
          // Add to the beginning of the array
          return [data.ban, ...prevBans];
        }
        return prevBans;
      });
      
      // Update statistics
      setBanStats(prevStats => ({
        ...prevStats,
        totalBans: prevStats.totalBans + 1,
        totalBansToday: prevStats.totalBansToday + 1,
        totalBansMonth: prevStats.totalBansMonth + 1
      }));
    });
    
    // Listen for ban removals
    const removeBanUnbind = addBanListener('ban-removed', (data: { ban_id: number }) => {
      setBans(prevBans => prevBans.filter(ban => ban.banId !== data.ban_id));
      
      // Update statistics
      setBanStats(prevStats => ({
        ...prevStats,
        totalBans: Math.max(0, prevStats.totalBans - 1),
        // We can't be sure if the ban was from today or this month, so don't update those
      }));
    });
    
    // Listen for ban updates
    const updateBanUnbind = addBanListener('ban-updated', (data: { ban: Ban }) => {
      setBans(prevBans => prevBans.map(ban => 
        ban.banId === data.ban.banId ? data.ban : ban
      ));
    });
    
    // Listen for statistics updates
    const statsUpdateUnbind = addBanListener('stats-update', (data: { stats: BanStatistics }) => {
      setBanStats(data.stats);
    });
    
    return () => {
      newBanUnbind();
      removeBanUnbind();
      updateBanUnbind();
      statsUpdateUnbind();
    };
  }, [addBanListener]);

  // Initial data loading effect
  useEffect(() => {
    fetchBans();
    fetchBanStatistics();
  }, [fetchBans, fetchBanStatistics]);

  return {
    bans,
    banStats,
    loading,
    error,
    fetchBans,
    fetchBanStatistics,
    createBan,
    updateBan,
    deleteBan
  };
}