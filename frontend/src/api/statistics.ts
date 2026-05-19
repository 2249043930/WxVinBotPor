import { http } from '@/utils/request'
import type { PaginationParams, PaginationData } from '@/types/common'

export interface MessageRecord {
  id: number
  msg_type: 'text' | 'image' | 'voice'
  image_content?: string
  msg_date: string
  inquirer?: string
  vin_code?: string
  car_model?: string
  source_group?: string
  raw_message?: string
}

export const statisticsApi = {
  getMessageRecords(params: any) {
    return http.get<PaginationData<MessageRecord>>('/v1/statistics/message', { params })
  }
}
