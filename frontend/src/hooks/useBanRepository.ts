import { useState, useEffect, useCallback } from 'react';
import { BanRepository, Ban, BanStatistics } from '@/repositories/banRepository';

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
      if (!result.error) {
        // Refresh bans and statistics after creation
        await Promise.all([
          fetchBans(true),
          fetchBanStatistics(true)
        ]);
      }
      return result;
    } catch (err) {
      console.error('Error in useBanRepository.createBan:', err);
      throw err;
    }
  }, [repository, fetchBans, fetchBanStatistics]);

  const updateBan = useCallback(async (banId: number, updateData: any) => {
    try {
      const result = await repository.updateBan(banId, updateData);
      if (!result.error) {
        // Refresh bans after update
        await fetchBans(true);
      }
      return result;
    } catch (err) {
      console.error('Error in useBanRepository.updateBan:', err);
      throw err;
    }
  }, [repository, fetchBans]);

  const deleteBan = useCallback(async (banId: number) => {
    try {
      const result = await repository.deleteBan(banId);
      if (!result.error) {
        // Refresh bans and statistics after deletion
        await Promise.all([
          fetchBans(true),
          fetchBanStatistics(true)
        ]);
      }
      return result;
    } catch (err) {
      console.error('Error in useBanRepository.deleteBan:', err);
      throw err;
    }
  }, [repository, fetchBans, fetchBanStatistics]);

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