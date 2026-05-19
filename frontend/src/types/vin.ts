export interface VinRecord {
  id: number
  date: string
  recognize_status: 'success' | 'fail'
  vin_code: string
  car_model: string
  source_group: string
  inquirer: string
  quoter: string
  is_quoted: boolean
  quote_time: string
  supplier: string
}

export interface VinRecordDetail extends VinRecord {
  raw_data?: any
  created_at?: string
  updated_at?: string
}
