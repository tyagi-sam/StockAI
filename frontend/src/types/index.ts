export interface User {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
} 