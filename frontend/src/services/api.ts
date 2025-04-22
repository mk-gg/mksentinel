import { BASE_URL } from '@/config/api';

interface ApiResponse<T> {
  data: T;
  error?: string;
}

export class ApiService {
  // Generic fetch method with error handling
  private static async fetchWithAuth<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${BASE_URL}${endpoint}`, {
        ...options,
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      return { data: data as T };
    } catch (error) {
      console.error(`Error fetching ${endpoint}:`, error);
      return { 
        data: {} as T, 
        error: error instanceof Error ? error.message : 'Unknown error occurred' 
      };
    }
  }

  // User/Auth endpoints
  static async getCurrentUser<T = unknown>() {
    return this.fetchWithAuth<T>('/current_user');
  }

  static async logout<T = unknown>() {
    return this.fetchWithAuth<T>('/logout');
  }

  // Ban endpoints
  static async getBans<T = unknown>() {
    return this.fetchWithAuth<T>('/api/bans');
  }

  static async getBanStatistics<T = unknown>() {
    return this.fetchWithAuth<T>('/api/bans/statistics');
  }

  static async createBan<T = unknown>(banData: any) {
    return this.fetchWithAuth<T>('/api/bans', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(banData),
    });
  }

  static async updateBan<T = unknown>(banId: number, updateData: any) {
    return this.fetchWithAuth<T>(`/api/ban/${banId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updateData),
    });
  }

  static async deleteBan<T = unknown>(banId: number) {
    return this.fetchWithAuth<T>(`/api/ban/${banId}`, {
      method: 'DELETE',
    });
  }
} 