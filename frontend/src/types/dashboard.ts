// 数据看板类型

export interface DashboardStats {
  totalVehicles: number
  monthNew: number
  weekNew: number
  todayNew: number
  groupCount: number
  llmSuccessRate: number
}

export interface StatCardData {
  title: string
  value: number | string
  trend?: number
  trendUp?: boolean
  icon: string
  iconColor: string
  suffix?: string
}

export interface PieChartData {
  name: string
  value: number
}

export interface BarChartData {
  name: string
  value: number
}

export interface LineChartData {
  date: string
  value: number
}

export interface ChartData {
  vehicleTypePie: PieChartData[]
  hotModelsBar: BarChartData[]
  displacementPie: PieChartData[]
  trendLine: LineChartData[]
}

export interface HotModelRank {
  rank: number
  modelName: string
  count: number
  trend: number
}

export interface RecentRecord {
  id: number
  vin: string
  model: string
  createTime: string
  status: number
}

export interface GroupActivityItem {
  group_name: string
  message_count: number
  percentage: number
}

export interface GroupActivityStats {
  total_vin_images: number
  period_days: number
  group_stats: GroupActivityItem[]
}
