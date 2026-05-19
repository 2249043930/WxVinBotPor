import { http } from '@/utils/request'
import type { User, UserForm } from '@/types/user'
import type { PaginationParams, PaginationData } from '@/types/common'

export const userApi = {
  // 获取用户列表
  getList(params: PaginationParams & { keyword?: string }) {
    return http.get<PaginationData<User>>('/v1/user/list', { params })
  },

  // 创建用户
  create(data: UserForm) {
    return http.post('/v1/user/create', data)
  },

  // 更新用户
  update(id: number, data: UserForm) {
    return http.put(`/v1/user/update/${id}`, data)
  },

  // 删除用户
  delete(id: number) {
    return http.delete(`/v1/user/delete/${id}`)
  },

  // 重置密码
  resetPassword(id: number) {
    return http.post(`/v1/user/reset-password/${id}`)
  },

  // 切换用户状态
  toggleStatus(id: number, status: number) {
    return http.put(`/v1/user/status/${id}`, { status })
  }
}
