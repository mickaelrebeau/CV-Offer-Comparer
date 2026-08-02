export interface AuthUser {
  id: string
  email: string
  full_name?: string | null
  avatar_url?: string | null
  created_at?: string | null
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: AuthUser
}
