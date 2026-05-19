// 车型配置类型

export interface MemberType {
  id: number
  name: string
  description?: string
  sort: number
}

export interface CarModel {
  id: number | string
  name: string
  brand?: string
  series?: string
  parentId?: number
  children?: CarModel[]
}

export interface Supplier {
  id: number
  wxid: string
  name: string
  selectedModels: number[]
}

export interface SupplierForm {
  id?: number
  wxid: string
  name: string
  selectedModels: number[]
}
