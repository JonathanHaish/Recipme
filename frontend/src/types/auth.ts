export interface User {
  id: number;
  username: string;
  email: string;
  is_staff?: boolean;
  is_superuser?: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  password2: string;
}

export interface LoginResponse {
  message: string;
  user: User;
}

export interface UserProfile {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile_image: string | null;
  profile_image_url: string | null;
  goals: string[];
  diet: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface UpdateProfileRequest {
  profile_image?: File | string | null;
  goals?: string[];
  diet?: string;
  description?: string;
}
