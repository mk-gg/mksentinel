import { ApiService } from '@/services/api';

export interface Ban {
  banId: number;
  capturedMessage: string;
  createdAt: string;
  memberId: string;
  reason: string;
  serverId: string;
}

export interface BanStatistics {
  totalBans: number;
  totalBansToday: number;
  totalBansMonth: number;
  totalBansYear: number;
  totalServers: number;
  totalMembers: number;
  monthlyTrend: any[];
  currentServerTime: string;
}

interface BansResponse {
  bans: Ban[];
}

export class BanRepository {
  private static instance: BanRepository;
  private cachedBans: Ban[] | null = null;
  private cachedStats: BanStatistics | null = null;
  private lastBansFetch: number = 0;
  private lastStatsFetch: number = 0;
  private cacheExpiration = 5 * 60 * 1000; // 5 minutes
  private statsCacheExpiration = 1 * 60 * 1000; // 1 minute for stats
  
  // Singleton pattern
  static getInstance(): BanRepository {
    if (!BanRepository.instance) {
      BanRepository.instance = new BanRepository();
    }
    return BanRepository.instance;
  }
  
  // Get all bans with cache
  async getBans(forceRefresh = false): Promise<{ bans: Ban[], error?: string }> {
    // Return cached data if valid and not forcing refresh
    if (!forceRefresh && 
        this.cachedBans && 
        (Date.now() - this.lastBansFetch < this.cacheExpiration)) {
      return { bans: this.cachedBans };
    }
    
    try {
      // Fetch fresh data
      const response = await ApiService.getBans<BansResponse>();
      
      if (response.error) {
        return { bans: this.cachedBans || [], error: response.error };
      }
      
      // Update cache
      this.cachedBans = response.data.bans;
      this.lastBansFetch = Date.now();
      
      return { bans: this.cachedBans };
    } catch (error) {
      console.error('Error fetching bans:', error);
      return { 
        bans: this.cachedBans || [], 
        error: error instanceof Error ? error.message : 'Failed to fetch bans' 
      };
    }
  }
  
  // Get ban statistics with cache
  async getBanStatistics(forceRefresh = false): Promise<{ stats: BanStatistics, error?: string }> {
    const defaultStats: BanStatistics = { 
      totalBans: 0, 
      totalBansToday: 0, 
      totalBansMonth: 0,
      totalBansYear: 0,
      totalServers: 0,
      totalMembers: 0,
      monthlyTrend: [],
      currentServerTime: new Date().toISOString()
    };
    
    // Return cached data if valid and not forcing refresh
    if (!forceRefresh && 
        this.cachedStats && 
        (Date.now() - this.lastStatsFetch < this.statsCacheExpiration)) {
      return { stats: this.cachedStats };
    }
    
    try {
      // Fetch fresh data
      const response = await ApiService.getBanStatistics<BanStatistics>();
      
      if (response.error) {
        return { stats: this.cachedStats || defaultStats, error: response.error };
      }
      
      // Update cache
      this.cachedStats = response.data;
      this.lastStatsFetch = Date.now();
      
      return { stats: this.cachedStats };
    } catch (error) {
      console.error('Error fetching ban statistics:', error);
      return { 
        stats: this.cachedStats || defaultStats, 
        error: error instanceof Error ? error.message : 'Failed to fetch statistics' 
      };
    }
  }
  
  // Create a new ban
  async createBan(banData: any) {
    const response = await ApiService.createBan(banData);
    if (!response.error) {
      // Invalidate cache
      this.invalidateCache();
    }
    return response;
  }
  
  // Update ban
  async updateBan(banId: number, updateData: any) {
    const response = await ApiService.updateBan(banId, updateData);
    if (!response.error) {
      // Invalidate cache
      this.invalidateCache();
    }
    return response;
  }
  
  // Delete ban
  async deleteBan(banId: number) {
    const response = await ApiService.deleteBan(banId);
    if (!response.error) {
      // Invalidate cache
      this.invalidateCache();
    }
    return response;
  }
  
  // Invalidate all caches
  invalidateCache() {
    this.cachedBans = null;
    this.cachedStats = null;
  }

  // Clear cache methods
  clearBansCache(): void {
    this.cachedBans = null;
    this.lastBansFetch = 0;
  }

  clearStatsCache(): void {
    this.cachedStats = null;
    this.lastStatsFetch = 0;
  }
} 