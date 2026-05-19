import { http } from '@/utils/request'
import type { Group, GroupForm, GroupNotification, VinRecord, VinRecordDetail } from '@/types/group'
import type { PaginationParams, PaginationData } from '@/types/common'

export const groupApi = {
  // 群管理
  getList(params: PaginationParams & { keyword?: string }) {
    // 转换参数名以匹配后端 API
    const apiParams: any = {
      page: params.page,
      page_size: params.pageSize,
    }
    if (params.keyword) apiParams.keyword = params.keyword
    return http.get<PaginationData<Group>>('/v1/group/list', { params: apiParams })
  },

  create(data: GroupForm) {
    return http.post('/v1/group/create', data)
  },

  update(id: number, data: GroupForm) {
    return http.put(`/v1/group/update/${id}`, data)
  },

  delete(id: number) {
    return http.delete(`/v1/group/delete/${id}`)
  },

  toggleStatus(id: number, status: number) {
    return http.put(`/v1/group/status/${id}`, { status })
  },

  // 通知配置
  getNotification(groupId: number) {
    return http.get<GroupNotification>(`/v1/group/notification/${groupId}`)
  },

  updateNotification(groupId: number, data: GroupNotification) {
    return http.put(`/v1/group/notification/${groupId}`, data)
  },

  // VIN记录
  getVinRecords(params: PaginationParams & any) {
    return http.get<PaginationData<VinRecord>>('/v1/vin/record', { params })
  },

  getVinRecordDetail(id: number) {
    return http.get<VinRecordDetail>(`/v1/vin/record/${id}`)
  },

  deleteVinRecord(id: number) {
    return http.delete(`/v1/vin/record/${id}`)
  },

  // 自动同步微信群
  syncGroups() {
    return http.post('/v1/group/sync')
  }
}
