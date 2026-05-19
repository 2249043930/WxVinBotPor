import { http } from '@/utils/request'
import type { PaginationData } from '@/types/common'

export interface LLMStats {
  success_count: number
  fail_count: number
  success_rate: number
}

export interface DailyStat {
  date: string
  count: number
  success_count: number
  fail_count: number
  success_rate: number
}

export const accountApi = {
  // 获取LLM识别统计数据
  getLLMStats() {
    return http.get<LLMStats>('/v1/account/llm-stats')
  },

  // 获取每日识别统计
  getDailyStats(params: { page?: number; page_size?: number; start_date?: string; end_date?: string }) {
    return http.get<PaginationData<DailyStat>>('/v1/account/daily-stats', { params })
  }
}
