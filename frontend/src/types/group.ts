// 厂群管理类型

export interface Group {
  id: number
  name: string
  groupId: string
  memberCount: number
  status: number
  createTime: string
}

export interface GroupForm {
  id?: number
  name: string
  groupId: string
  status: number
}

export interface GroupNotification {
  inquiry: boolean
  quote: boolean
  shipping: boolean
  deal: boolean
  workTimeStart: string
  workTimeEnd: string
}

export interface VinRecord {
  id: number
  date: string
  status: number
  vin: string
  model: string
  sourceGroup: string
  inquirer: string
  quoter?: string
  isQuoted: boolean
  quoteTime?: string
  supplier?: string
}

export interface VinRecordDetail {
  id: number
  vin: string
  model: string
  rawImage: string
  resultJson: string
  chatRecords: ChatRecord[]
}

export interface ChatRecord {
  id: number
  sender: string
  content: string
  time: string
  type: 'text' | 'image'
}
