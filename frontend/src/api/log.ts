import { http } from '@/utils/request'
import type { PaginationParams, PaginationData } from '@/types/common'

export interface LogRecord {
  id: number
  userNickname: string
  ip: string
  location: string
  os: string
  browser: string
  loginTime: string
  operation: string
}

export const logApi = {
  getList(params: PaginationParams & { 
    dateRange?: [string, string]
    userId?: number
    ip?: string
    operationType?: string
  }) {
    // 转换参数名以匹配后端 API
    const apiParams: any = {
      page: params.page,
      page_size: params.pageSize,
    }
    if (params.dateRange) {
      apiParams.start_date = params.dateRange[0]
      apiParams.end_date = params.dateRange[1]
    }
    if (params.userId) apiParams.user_id = params.userId
    if (params.ip) apiParams.ip_address = params.ip
    if (params.operationType) apiParams.operation_type = params.operationType
    
    return http.get<PaginationData<LogRecord>>('/v1/log/login', { params: apiParams })
  }
}
