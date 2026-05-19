// 认证相关工具函数

const TOKEN_KEY = 'token'
const USER_KEY = 'user_info'

export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY)
}

export const setToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token)
}

export const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY)
}

export const getUserInfo = () => {
  const userStr = localStorage.getItem(USER_KEY)
  return userStr ? JSON.parse(userStr) : null
}

export const setUserInfo = (userInfo: any): void => {
  localStorage.setItem(USER_KEY, JSON.stringify(userInfo))
}

export const removeUserInfo = (): void => {
  localStorage.removeItem(USER_KEY)
}

export const clearAuth = (): void => {
  removeToken()
  removeUserInfo()
}

export const isAuthenticated = (): boolean => {
  return !!getToken()
}
