// 通用类型定义

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PaginationParams {
  page: number
  pageSize: number
}

export interface PaginationData<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

export interface SelectOption {
  label: string
  value: string | number
}

export type StatusType = 'success' | 'warning' | 'danger' | 'info'
