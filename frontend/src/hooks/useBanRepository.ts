import { useState, useEffect, useCallback } from 'react';
import { BanRepository, Ban, BanStatistics } from '@/repositories/banRepository';

// Define the response type for createBan
interface CreateBanResponse {
  ban?: Ban;
  message?: string;
}

export function useBanRepository() {
  const repository = BanRepository.getInstance();
  const [bans, setBans] = useState<Ban[]>([]);
  const [banStats, setBanStats] = useState<BanStatistics>({ totalBans: 0, totalBansToday: 0, totalBansMonth: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
        
        // Quietly refresh the data in the background to ensure consistency
        setTimeout(() => {
          Promise.all([
            repository.getBans(true).then(result => {
              if (!result.error) {
                setBans(result.bans);
              }
            }),
            repository.getBanStatistics(true).then(result => {
              if (!result.error) {
                setBanStats(result.stats);
              }
            })
          ]);
        }, 2000);
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
        
        // Quietly refresh the data in the background to ensure consistency
        // but don't wait for it or show loading indicators
        setTimeout(() => {
          repository.getBans(true).then(result => {
            if (!result.error) {
              setBans(result.bans);
            }
          });
        }, 2000);
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
            // We can't be sure if the ban was from today or this month, so refresh those stats
          }));
        }
        
        // Quietly refresh the statistics to get accurate data
        fetchBanStatistics(true);
        
        // Quietly refresh the data in the background to ensure consistency
        setTimeout(() => {
          repository.getBans(true).then(result => {
            if (!result.error) {
              setBans(result.bans);
            }
          });
        }, 2000);
      }
      
      return result;
    } catch (err) {
      console.error('Error in useBanRepository.deleteBan:', err);
      throw err;
    }
  }, [repository, fetchBanStatistics, banStats]);

  // Initial data loading effect
  useEffect(() => {
    fetchBans();
  }, [fetchBans]);

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