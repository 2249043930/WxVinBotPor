import { http } from '@/utils/request'
import type { MemberType, CarModel, Supplier, SupplierForm } from '@/types/carModel'
import type { PaginationParams, PaginationData } from '@/types/common'

export const carModelApi = {
  // 成员类型
  getMemberTypes() {
    return http.get<MemberType[]>('/v1/car-model/member-type')
  },

  createMemberType(data: { name: string; description?: string }) {
    return http.post('/v1/car-model/member-type', data)
  },

  updateMemberType(id: number, data: { name: string; description?: string }) {
    return http.put(`/v1/car-model/member-type/${id}`, data)
  },

  deleteMemberType(id: number) {
    return http.delete(`/v1/car-model/member-type/${id}`)
  },

  // 车型树
  getCarModelTree() {
    return http.get<{code: number; message: string; data: CarModel[]}>('/v1/car-model/car-model').then(res => res)
  },

  // 创建车型
  createCarModel(data: { name: string; brand?: string; series?: string; displacement?: string; year?: string }) {
    return http.post<{code: number; message: string; data: CarModel}>('/v1/car-model/car-model', data)
  },

  // 更新车型
  updateCarModel(id: number, data: { name: string; brand?: string; series?: string; displacement?: string; year?: string }) {
    return http.put<{code: number; message: string; data: CarModel}>(`/v1/car-model/car-model/${id}`, data)
  },

  // 删除车型
  deleteCarModel(id: number) {
    return http.delete<{code: number; message: string}>(`/v1/car-model/car-model/${id}`)
  },

  // 根据车型名称获取供应商（用于艾特功能）
  getSuppliersByModelName(modelName: string) {
    return http.get<{code: number; message: string; data: Supplier[]}>('/v1/car-model/car-model/suppliers', {
      params: { model_name: modelName }
    }).then(res => res.data || [])
  },

  // 汽配商
  getSuppliers(params: PaginationParams) {
    return http.get<PaginationData<Supplier>>('/v1/car-model/supplier', { params })
  },

  createSupplier(data: SupplierForm) {
    return http.post('/v1/car-model/supplier', data)
  },

  updateSupplier(id: number, data: SupplierForm) {
    return http.put(`/v1/car-model/supplier/${id}`, data)
  },

  deleteSupplier(id: number) {
    return http.delete(`/v1/car-model/supplier/${id}`)
  }
}
