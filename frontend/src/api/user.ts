import { requestWithAuth,requestNoAuth} from '@/utils/request'
import type {
  UserRegisterRequest,
  UserLoginRequest,
  UserUpdateRequest,
  PasswordChangeRequest,
  UserLoginResponse,
  UserResponseItem
} from '@/types/user'

// 注册
export const registerUser = (data: UserRegisterRequest): Promise<null> => {
  return requestNoAuth({
    url: '/user/register',
    method: 'POST',
    data,
  })
}

// 登录
export const loginUser = (data: UserLoginRequest): Promise<UserLoginResponse> => {
  return requestNoAuth({
    url: '/user/login',
    method: 'POST',
    data
  })
}

// 获取用户资料
export const getUserProfile = (): Promise<UserResponseItem> => {
  return requestWithAuth({
    url: '/user/profile/view',
    method: 'POST'
  })
}

// 更新用户资料
export const updateUserProfile = (data: UserUpdateRequest): Promise<null> => {
  return requestWithAuth({
    url: '/user/profile/update',
    method: 'POST',
    data
  })
}

// 修改密码
export const changePassword = (data: PasswordChangeRequest): Promise<null> => {
  return requestWithAuth({
    url: '/user/password/reset',
    method: 'POST',
    data
  })
}

// 注销账户
export const deleteAccount = (): Promise<null> => {
  return requestWithAuth({
    url: '/user/delete',
    method: 'POST'
  })
}
