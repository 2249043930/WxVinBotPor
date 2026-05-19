// 用户相关类型

export interface User {
  id: number
  nickname: string
  username: string
  phone?: string
  email?: string
  remark?: string
  status: number
  createTime: string
}

export interface UserForm {
  id?: number
  nickname: string
  username: string
  password?: string
  phone?: string
  email?: string
  remark?: string
}

export interface LoginForm {
  username: string
  password: string
  captcha: string
  remember?: boolean
}

export interface UserInfo {
  id: number
  nickname: string
  username: string
  avatar?: string
  roles: string[]
}
