import { http } from '@/utils/request'

export interface LLMConfig {
  apiKey: string
}

export interface VINRecognitionResult {
  vin: string
  greeting: string
  error?: string
}

export const llmApi = {
  getConfig() {
    return http.get<LLMConfig>('/v1/llm/config')
  },

  updateConfig(data: LLMConfig) {
    return http.put('/v1/llm/config', data)
  },

  // 识别VIN
  recognizeVIN(imageBase64: string) {
    return http.post<VINRecognitionResult>('/v1/llm/recognize', { image: imageBase64 })
  }
}
