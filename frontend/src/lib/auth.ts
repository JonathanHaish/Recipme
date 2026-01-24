import type {
  User,
  LoginRequest,
  RegisterRequest,
  LoginResponse,
} from '@/types/auth';

const API_URL = typeof window !== 'undefined' 
  ? (window as any).ENV?.API_URL || 'http://localhost:8000'
  : 'http://localhost:8000';

const AUTH_ENDPOINTS = {
  register: `${API_URL}/api/auth/register`,
  login: `${API_URL}/api/auth/login`,
  logout: `${API_URL}/api/auth/logout`,
  refresh: `${API_URL}/api/auth/refresh`,
  me: `${API_URL}/api/auth/me`,
};

// API client with automatic token refresh (using httpOnly cookies)
class APIClient {
  private isRefreshing = false;
  private refreshSubscribers: Array<() => void> = [];

  private subscribeTokenRefresh(callback: () => void): void {
    this.refreshSubscribers.push(callback);
  }

  private onTokenRefreshed(): void {
    this.refreshSubscribers.forEach((callback) => callback());
    this.refreshSubscribers = [];
  }

  async request<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Don't set Content-Type for requests without body (like DELETE) or FormData
    const hasBody = options.body !== undefined && options.body !== null;
    const isFormData = options.body instanceof FormData;
    const headers: HeadersInit = {
      ...(hasBody && !isFormData && { 'Content-Type': 'application/json' }),
      ...options.headers,
    };

    // Cookies are sent automatically with credentials: 'include'
    let response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include', // Important: sends cookies with request
    });

    // Endpoints that should not trigger token refresh
    const noRefreshEndpoints = ['/login', '/register', '/forgot-password', '/reset-password'];
    const shouldSkipRefresh = noRefreshEndpoints.some(endpoint => url.includes(endpoint));

    // Handle token refresh on 401, but not for auth endpoints
    if (response.status === 401 && !shouldSkipRefresh) {
      if (!this.isRefreshing) {
        this.isRefreshing = true;
        try {
          await this.refreshAccessToken();
          this.isRefreshing = false;
          this.onTokenRefreshed();
          
          // Retry original request (new cookie will be sent automatically)
          response = await fetch(url, {
            ...options,
            headers,
            credentials: 'include',
          });
        } catch (error) {
          this.isRefreshing = false;
          throw new Error('Session expired. Please login again.');
        }
      } else {
        // Wait for token refresh to complete
        await new Promise<void>((resolve) => {
          this.subscribeTokenRefresh(() => {
            resolve();
          });
        });
        
        // Retry with refreshed token
        response = await fetch(url, {
          ...options,
          headers,
          credentials: 'include',
        });
      }
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Request failed' }));
      
      // Handle Django REST Framework validation errors (field-based)
      if (typeof error === 'object' && !error.error && !error.message) {
        // Convert field errors to readable message
        const fieldErrors = Object.entries(error)
          .map(([field, messages]) => {
            const errorMessages = Array.isArray(messages) ? messages : [messages];
            return errorMessages.join(' ');
          })
          .join(' ');
        
        throw new Error(fieldErrors || 'Request failed');
      }
      
      throw new Error(error.error || error.message || 'Request failed');
    }

    // Handle empty responses (e.g., 204 No Content for DELETE requests)
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      // No content or not JSON, return undefined for void responses
      return undefined as T;
    }

    // Check if response has content before parsing
    const text = await response.text();
    if (!text || text.trim().length === 0) {
      return undefined as T;
    }

    return JSON.parse(text) as T;
  }

  private async refreshAccessToken(): Promise<void> {
    const response = await fetch(AUTH_ENDPOINTS.refresh, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Send refresh token cookie
    });

    if (!response.ok) {
      throw new Error('Failed to refresh token');
    }
    
    // New access token cookie is set automatically by the server
  }
}

const apiClient = new APIClient();

// Export apiClient for use in other API modules
export { apiClient };

// Auth API functions
export const authAPI = {
  /**
   * Register a new user
   */
  register: async (data: RegisterRequest): Promise<{ message: string }> => {
    return apiClient.request(AUTH_ENDPOINTS.register, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Login - tokens are set as httpOnly cookies by the server
   */
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    return apiClient.request<LoginResponse>(
      AUTH_ENDPOINTS.login,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
    // Cookies are set automatically by the server
  },

  /**
   * Logout - blacklists refresh token and clears cookies
   */
  logout: async (): Promise<void> => {
    try {
      await apiClient.request(AUTH_ENDPOINTS.logout, {
        method: 'POST',
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
    // Cookies are cleared automatically by the server
  },

  /**
   * Get current authenticated user
   */
  getMe: async (): Promise<User> => {
    return apiClient.request<User>(AUTH_ENDPOINTS.me);
  },

  /**
   * Check if user is authenticated by attempting to get user data
   */
  isAuthenticated: async (): Promise<boolean> => {
    try {
      await authAPI.getMe();
      return true;
    } catch {
      return false;
    }
  },

  /**
   * Request password reset - sends email with reset link
   */
  forgotPassword: async (email: string): Promise<{ message: string }> => {
    return apiClient.request(`${API_URL}/api/auth/forgot-password`, {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  /**
   * Reset password using token from email
   */
  resetPassword: async (data: { uid: string; token: string; password: string; password2: string }): Promise<{ message: string }> => {
    return apiClient.request(`${API_URL}/api/auth/reset-password`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

