import { http } from '@/utils/request'
import type { PaginationData } from '@/types/common'
import type { VinRecord, VinRecordDetail } from '@/types/vin'

export const vinApi = {
  // 获取车架号记录列表
  getRecords(params: any) {
    return http.get<PaginationData<VinRecord>>('/v1/vin/record', { params })
  },

  // 获取车架号记录详情
  getDetail(id: number) {
    return http.get<VinRecordDetail>(`/v1/vin/record/${id}`)
  },

  // 删除车架号记录
  deleteRecord(id: number) {
    return http.delete(`/v1/vin/record/${id}`)
  }
}
