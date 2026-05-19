import { http } from '@/utils/request'

export interface ApiConfig {
  id?: number
  config_type: string
  name: string
  api_key?: string
  api_base?: string
  api_secret?: string
  model?: string
  temperature?: string
  max_tokens?: number
  prompt_template?: string
  db_host?: string
  db_port?: number
  db_name?: string
  db_user?: string
  db_password?: string
  wx_id?: string
  api_url?: string
  is_active: boolean
  is_default: boolean
  description?: string
  created_at?: string
  updated_at?: string
}

export interface ApiConfigList {
  list: ApiConfig[]
  total: number
}

export interface VINRecognitionResult {
  vin: string
  greeting: string
  error?: string
}

export const apiConfigApi = {
  // 获取配置列表
  getList(config_type?: string, page = 1, page_size = 10) {
    return http.get<ApiConfigList>('/v1/api-config/list', {
      params: { config_type, page, page_size }
    })
  },

  // 获取单个配置
  getById(id: number) {
    return http.get<ApiConfig>(`/v1/api-config/${id}`)
  },

  // 创建配置
  create(data: ApiConfig) {
    return http.post<ApiConfig>('/v1/api-config/create', data)
  },

  // 更新配置
  update(id: number, data: Partial<ApiConfig>) {
    return http.put<ApiConfig>(`/v1/api-config/update/${id}`, data)
  },

  // 删除配置
  delete(id: number) {
    return http.delete(`/v1/api-config/delete/${id}`)
  },

  // 识别VIN
  recognizeVIN(imageBase64: string, configId?: number) {
    return http.post<VINRecognitionResult>('/v1/api-config/recognize', {
      image: imageBase64,
      config_id: configId
    })
  }
}
