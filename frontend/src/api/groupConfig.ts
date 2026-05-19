import { http } from '@/utils/request'
import type { PaginationData } from '@/types/common'

export interface GroupConfig {
  id: number
  group_id: string
  group_name: string
  customer_service_wxid: string
  customer_service_name: string
  model_suppliers: ModelSupplier[]
  created_at: string
  updated_at: string
}

export interface ModelSupplier {
  id: number
  car_model_id: number
  car_model_name: string
  supplier_id: number
  supplier_wxid: string
  supplier_name: string
}

export interface GroupOption {
  group_id: string
  group_name: string
}

export interface GroupMember {
  wxid: string
  nick: string
  group_nick: string
  display_name: string
}

export const groupConfigApi = {
  // 获取可用于配置的群聊列表（只返回已开启的群）
  getGroups() {
    return http.get<GroupOption[]>('/v1/group-config/groups')
  },

  // 获取群聊配置列表
  getList(params: { page: number; page_size: number }) {
    return http.get<PaginationData<GroupConfig>>('/v1/group-config/list', { params })
  },

  // 获取单个群聊配置详情
  getDetail(groupId: string) {
    return http.get<GroupConfig>(`/v1/group-config/detail/${groupId}`).catch(err => {
      // 404表示配置不存在，返回null
      if (err.response?.status === 404) {
        return null
      }
      throw err
    })
  },

  // 创建群聊配置
  create(data: {
    group_id: string
    group_name: string
    customer_service_wxid: string
    customer_service_name: string
    model_suppliers: { car_model_id: number; supplier_id: number }[]
  }) {
    return http.post<GroupConfig>('/v1/group-config/create', data)
  },

  // 更新群聊配置
  update(configId: number, data: {
    group_name?: string
    customer_service_wxid?: string
    customer_service_name?: string
    model_suppliers?: { car_model_id: number; supplier_id: number }[]
  }) {
    return http.put<GroupConfig>(`/v1/group-config/update/${configId}`, data)
  },

  // 删除群聊配置
  delete(configId: number) {
    return http.delete(`/v1/group-config/delete/${configId}`)
  },

  // 获取群中某个车型的供应商
  getSupplierByModel(groupId: string, carModelId: number) {
    return http.get<{ supplier_wxid: string; supplier_name: string }>('/v1/group-config/suppliers-by-model', {
      params: { group_id: groupId, car_model_id: carModelId }
    })
  },

  // 获取群成员列表，支持模糊搜索
  getGroupMembers(groupId: string, keyword?: string) {
    return http.get<GroupMember[]>('/v1/group-config/group-members', {
      params: { group_id: groupId, keyword }
    }).then(res => {
      // 拦截器返回的是 res.data，直接是数组
      if (Array.isArray(res)) {
        return res
      }
      return []
    })
  }
}
