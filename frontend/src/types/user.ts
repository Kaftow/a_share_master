import type { ISODateString, ISODateTimeString } from '@/types/common';
export type UserStatus = 'enabled' | 'disabled' | 'banned';
export type UserRole = 'user' | 'admin' | 'moderator';

export interface UserLoginRequest {
  username: string;
  password: string;
}

export interface UserRegisterRequest {
  username: string;
  email: string;
  password: string;
  nickname?: string;
}

export interface UserUpdateRequest {
  nickname?: string;
  email?: string;
  avatar_id?: number;
  gender?: string;
  birth_date?: ISODateString;
  country?: string;
}

export interface PasswordChangeRequest {
  old_password: string;
  new_password: string;
}

export interface UserResponseItem {
  username: string;
  email?: string;
  nickname?: string;
  avatar_id?: number;
  gender?: string;
  birth_date?: ISODateString;
  country?: string;
  status?: UserStatus;
  role?: UserRole;
  last_login?: ISODateTimeString;
  created_at: ISODateTimeString;
}

export interface UserLoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserResponseItem;
}
