import { ApiService } from '@/services/api';
import { BASE_URL } from '@/config/api';

export interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
}

interface UserResponse {
  user: User;
}

export class AuthRepository {
  private static instance: AuthRepository;
  private cachedUser: User | null = null;
  private lastUserFetch: number = 0;
  private cacheExpiration = 10 * 60 * 1000; // 10 minutes
  
  // Singleton pattern
  static getInstance(): AuthRepository {
    if (!AuthRepository.instance) {
      AuthRepository.instance = new AuthRepository();
    }
    return AuthRepository.instance;
  }
  
  // Get current user with cache
  async getCurrentUser(forceRefresh = false): Promise<{ user: User | null, error?: string }> {
    // Return cached data if valid and not forcing refresh
    if (!forceRefresh && 
        this.cachedUser && 
        (Date.now() - this.lastUserFetch < this.cacheExpiration)) {
      return { user: this.cachedUser };
    }
    
    // Fetch fresh data
    const response = await ApiService.getCurrentUser<UserResponse>();
    
    if (response.error) {
      return { user: null, error: response.error };
    }
    
    // Update cache if user exists
    if (response.data.user) {
      this.cachedUser = response.data.user;
      this.lastUserFetch = Date.now();
      return { user: this.cachedUser };
    }
    
    return { user: null };
  }
  
  // Log out user
  async logout(): Promise<{ success: boolean, error?: string }> {
    const response = await ApiService.logout<{ status: string, message?: string }>();
    
    if (response.error) {
      return { success: false, error: response.error };
    }
    
    if (response.data.status === 'success') {
      // Clear cached user
      this.cachedUser = null;
      return { success: true };
    }
    
    return { success: false, error: response.data.message || 'Unknown error' };
  }
  
  // Helper method to start Google OAuth flow
  redirectToGoogleAuth() {
    // Using the imported BASE_URL directly instead of require
    window.location.href = `${BASE_URL}/authorize/google`;
  }
  
  // Invalidate user cache
  invalidateCache() {
    this.cachedUser = null;
  }
} 