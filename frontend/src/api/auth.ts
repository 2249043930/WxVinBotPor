import { http } from '@/utils/request'
import type { LoginForm, UserInfo } from '@/types/user'

export const authApi = {
  // 用户登录
  login(data: LoginForm) {
    return http.post<{ token: string; userInfo: UserInfo }>('/v1/auth/login', data)
  },

  // 用户登出
  logout() {
    return http.post('/v1/auth/logout')
  },

  // 获取当前用户信息
  getUserInfo() {
    return http.get<UserInfo>('/v1/auth/info')
  }
}
