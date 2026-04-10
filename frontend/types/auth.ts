export interface AuthUser {
  id: number;
  fullName: string;
  email: string;
  role: string;
  status: string;
}

export interface TokenPayload {
  accessToken: string;
  tokenType: string;
}
