import { http } from '@/utils/request'
import type { DashboardStats, ChartData, HotModelRank, RecentRecord, GroupActivityStats } from '@/types/dashboard'

export const dashboardApi = {
  // 获取看板统计数据
  getStats() {
    return http.get<DashboardStats>('/v1/dashboard/stats')
  },

  // 获取图表数据
  getCharts() {
    return http.get<ChartData>('/v1/dashboard/charts')
  },

  // 获取热门车型排行
  getHotModels() {
    return http.get<HotModelRank[]>('/v1/dashboard/hot-models')
  },

  // 获取最近识别记录
  getRecentRecords() {
    return http.get<RecentRecord[]>('/v1/dashboard/recent-records')
  },

  // 获取群活跃度统计
  getGroupActivityStats(days: number = 30, limit: number = 10) {
    return http.get<GroupActivityStats>('/v1/statistics/group-activity', {
      params: { days, limit }
    })
  }
}
