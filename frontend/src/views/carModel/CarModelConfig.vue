<template>
  <div class="page-container">
    <!-- 搜索栏 -->
    <div class="search-form-container">
      <el-form :model="query" inline>
        <el-form-item>
          <el-input
            v-model="query.keyword"
            placeholder="搜索群名称/ID"
            clearable
            style="width: 300px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 操作栏 -->
    <div class="table-operations">
      <el-button type="success" @click="handleSyncGroups" :loading="syncLoading">
        <el-icon><Refresh /></el-icon>同步群聊信息
      </el-button>
    </div>
    
    <!-- 数据表格 -->
    <el-card>
      <el-table :data="filteredGroups" stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="group_name" label="群聊名称" show-overflow-tooltip />
        <el-table-column prop="group_id" label="群ID" show-overflow-tooltip />
        <el-table-column label="同步时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.sync_time) }}
          </template>
        </el-table-column>
        <el-table-column label="配置状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_configured" type="success">已配置</el-tag>
            <el-tag v-else type="danger">未配置</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="配置" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleConfig(row)">
              <el-icon><Setting /></el-icon>配置
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleViewDetail(row)">
              <el-icon><View /></el-icon>查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <Pagination
        :total="filteredTotal"
        :page="query.page"
        :limit="query.pageSize"
        @pagination="handlePagination"
      />
    </el-card>

    <!-- 配置弹窗 -->
    <el-dialog
      v-model="configDialogVisible"
      title="群聊配置"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-card class="config-card">
        <!-- 群聊信息 -->
        <div class="group-info">
          <h4>{{ currentGroup?.group_name }}</h4>
          <el-tag size="small" type="info">{{ currentGroup?.group_id }}</el-tag>
        </div>

        <!-- 专属客服配置 -->
        <div class="config-section">
          <div class="section-title">
            <span>专属客服</span>
            <el-tag v-if="configForm.customer_service_wxid" type="success">已配置</el-tag>
            <el-tag v-else type="info">未配置</el-tag>
          </div>
          <el-select
            v-model="configForm.customer_service_wxid"
            placeholder="请选择客服"
            style="width: 100%"
            clearable
            filterable
            @visible-change="(visible) => visible && loadCustomerMembers()"
            :loading="loadingCustomerMembers"
          >
            <el-option
              v-for="member in customerSearchResults"
              :key="member.wxid"
              :label="member.display_name"
              :value="member.wxid"
            >
              <div class="member-option">
                <span class="member-name">{{ member.nick || member.group_nick }}</span>
                <span class="member-wxid">{{ member.wxid }}</span>
              </div>
            </el-option>
          </el-select>
        </div>

        <!-- 车型供应商配置 -->
        <div class="config-section">
          <div class="section-title">
            <span>车型供应商绑定</span>
            <el-button type="primary" link @click="addModelSupplier">
              <el-icon><Plus /></el-icon>添加绑定
            </el-button>
          </div>
          
          <div
            v-for="(item, index) in configForm.model_suppliers"
            :key="index"
            class="model-supplier-row"
          >
            <el-tree-select
              v-model="item.car_model_id"
              :data="carModelTree"
              placeholder="选择车型"
              style="width: 260px"
              filterable
              :props="{ label: 'name', value: 'id', children: 'children' }"
              :render-after-expand="true"
              default-expand-all
              popper-class="car-model-tree-dropdown"
              :teleported="false"
            />
            
            <el-select
              v-model="item.supplier_wxid"
              placeholder="选择供应商"
              style="width: 45%; margin-left: 10px"
              clearable
              filterable
              @visible-change="(visible) => visible && loadSupplierMembers(index)"
              :loading="item.loadingMembers"
            >
              <el-option
                v-for="member in item.supplier_search_results"
                :key="member.wxid"
                :label="member.display_name"
                :value="member.wxid"
              >
                <div class="member-option">
                  <span class="member-name">{{ member.nick || member.group_nick }}</span>
                  <span class="member-wxid">{{ member.wxid }}</span>
                </div>
              </el-option>
            </el-select>
            
            <el-button
              type="danger"
              link
              @click="removeModelSupplier(index)"
              style="margin-left: 10px"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          
          <el-empty v-if="configForm.model_suppliers.length === 0" description="暂无车型供应商绑定" />
        </div>
      </el-card>

      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveConfig" :loading="savingConfig">保存配置</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="群聊配置详情"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-card class="detail-card" v-if="currentDetail">
        <!-- 群聊基本信息 -->
        <div class="detail-section">
          <div class="section-header">
            <h4>群聊信息</h4>
            <el-tag v-if="currentDetail.is_configured" type="success">已配置</el-tag>
            <el-tag v-else type="danger">未配置</el-tag>
          </div>
          <div class="detail-item">
            <span class="label">群聊名称：</span>
            <span class="value">{{ currentDetail.group_name }}</span>
          </div>
          <div class="detail-item">
            <span class="label">群ID：</span>
            <span class="value">{{ currentDetail.group_id }}</span>
          </div>
          <div class="detail-item">
            <span class="label">同步时间：</span>
            <span class="value">{{ formatDate(currentDetail.sync_time) }}</span>
          </div>
        </div>

        <!-- 专属客服信息 -->
        <div class="detail-section" v-if="currentDetail.config">
          <div class="section-header">
            <h4>专属客服</h4>
          </div>
          <div class="detail-item" v-if="currentDetail.config.customer_service_name">
            <span class="label">客服名称：</span>
            <span class="value">{{ currentDetail.config.customer_service_name }}</span>
          </div>
          <div class="detail-item" v-if="currentDetail.config.customer_service_wxid">
            <span class="label">客服微信ID：</span>
            <span class="value">{{ currentDetail.config.customer_service_wxid }}</span>
          </div>
          <el-empty v-else description="未配置专属客服" />
        </div>

        <!-- 车型供应商绑定 -->
        <div class="detail-section" v-if="currentDetail.config && currentDetail.config.model_suppliers && currentDetail.config.model_suppliers.length > 0">
          <div class="section-header">
            <h4>车型供应商绑定</h4>
            <el-tag type="info">{{ currentDetail.config.model_suppliers.length }} 个绑定</el-tag>
          </div>
          <div class="supplier-list">
            <div 
              v-for="(item, index) in currentDetail.config.model_suppliers" 
              :key="index"
              class="supplier-item"
            >
              <div class="supplier-info">
                <el-tag size="small" type="primary">{{ item.car_model_name || '未知车型' }}</el-tag>
                <span class="supplier-name">{{ item.supplier_name || '未知供应商' }}</span>
              </div>
              <span class="supplier-wxid">{{ item.supplier_wxid }}</span>
            </div>
          </div>
        </div>
        <div class="detail-section" v-else-if="currentDetail.is_configured">
          <div class="section-header">
            <h4>车型供应商绑定</h4>
          </div>
          <el-empty description="未配置车型供应商绑定" />
        </div>
      </el-card>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEditFromDetail">编辑配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, View, Setting, Plus, Delete } from '@element-plus/icons-vue'
import Pagination from '@/components/common/Pagination.vue'
import { groupConfigApi } from '@/api/groupConfig'
import { carModelApi } from '@/api/carModel'
import type { GroupOption, GroupMember } from '@/api/groupConfig'
import type { CarModel } from '@/types/carModel'

const loading = ref(false)
const syncLoading = ref(false)
const syncedGroups = ref<(GroupOption & { sync_time?: string })[]>([])

const query = reactive({
  keyword: '',
  page: 1,
  pageSize: 10
})

// 配置弹窗相关
const configDialogVisible = ref(false)
const currentGroup = ref<GroupOption & { sync_time?: string } | null>(null)
const savingConfig = ref(false)

// 客服搜索
const customerSearchResults = ref<GroupMember[]>([])

// 群成员列表（用于客服和供应商选择）
const loadingCustomerMembers = ref(false)

// 缓存当前群的成员列表
const currentGroupMembers = ref<GroupMember[]>([])

// 车型列表（树形结构）
const carModelTree = ref<CarModel[]>([])

// 详情弹窗相关
const detailDialogVisible = ref(false)
const currentDetail = ref<(GroupOption & { sync_time?: string; is_configured?: boolean; config?: any }) | null>(null)

// 配置表单
const configForm = reactive({
  customer_service_wxid: '',
  customer_service_name: '',
  model_suppliers: [] as {
    car_model_id: number
    supplier_wxid: string
    supplier_name: string
    supplier_search_results: GroupMember[]
    loadingMembers: boolean
  }[]
})

// 根据关键词过滤的群聊列表
const filteredGroups = computed(() => {
  let result = syncedGroups.value
  
  // 关键词过滤
  if (query.keyword) {
    const keyword = query.keyword.toLowerCase()
    result = result.filter(group => 
      group.group_name.toLowerCase().includes(keyword) ||
      group.group_id.toLowerCase().includes(keyword)
    )
  }
  
  // 分页截取
  const start = (query.page - 1) * query.pageSize
  const end = start + query.pageSize
  return result.slice(start, end)
})

// 过滤后的总数（用于分页显示）
const filteredTotal = computed(() => {
  if (!query.keyword) return syncedGroups.value.length
  const keyword = query.keyword.toLowerCase()
  return syncedGroups.value.filter(group => 
    group.group_name.toLowerCase().includes(keyword) ||
    group.group_id.toLowerCase().includes(keyword)
  ).length
})

const formatDate = (date?: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const loadSyncedGroups = async () => {
  loading.value = true
  try {
    const saved = localStorage.getItem('synced_groups')
    if (saved) {
      const groups = JSON.parse(saved)
      // 检查每个群的配置状态
      const groupsWithStatus = await Promise.all(
        groups.map(async (group: GroupOption & { sync_time?: string }) => {
          try {
            const config = await groupConfigApi.getDetail(group.group_id)
            return {
              ...group,
              is_configured: !!config
            }
          } catch (error) {
            return {
              ...group,
              is_configured: false
            }
          }
        })
      )
      syncedGroups.value = groupsWithStatus
    }
  } catch (error) {
    console.error('加载同步记录失败', error)
  } finally {
    loading.value = false
  }
}

const loadCarModels = async () => {
  try {
    const res = await carModelApi.getCarModelTree()
    console.log('车型API返回数据:', res)
    // API返回格式: {code: 0, message: "success", data: [...]}
    if (res && res.code === 0 && Array.isArray(res.data)) {
      carModelTree.value = res.data
    } else if (Array.isArray(res)) {
      // 兼容直接返回数组的情况
      carModelTree.value = res
    }
    console.log('车型树:', carModelTree.value)
  } catch (error) {
    console.error('加载车型失败', error)
  }
}

const handleSyncGroups = async () => {
  syncLoading.value = true
  try {
    const groups = await groupConfigApi.getGroups()
    
    const synced = groups.map(g => ({
      ...g,
      sync_time: new Date().toISOString()
    }))
    
    localStorage.setItem('synced_groups', JSON.stringify(synced))
    syncedGroups.value = synced
    
    ElMessage.success(`成功同步 ${groups.length} 个群聊`)
  } catch (error) {
    console.error('同步群聊失败', error)
    ElMessage.error('同步失败，请检查网络连接')
  } finally {
    syncLoading.value = false
  }
}

const handleSearch = () => {
  query.page = 1
}

const handleReset = () => {
  query.keyword = ''
  query.page = 1
}

// 查看详情
const handleViewDetail = async (row: GroupOption & { sync_time?: string }) => {
  currentDetail.value = {
    ...row,
    is_configured: false,
    config: null
  }
  
  // 加载配置详情
  try {
    const config = await groupConfigApi.getDetail(row.group_id)
    if (config) {
      currentDetail.value.is_configured = true
      currentDetail.value.config = config
    }
  } catch (error) {
    // 没有配置
    currentDetail.value.is_configured = false
  }
  
  detailDialogVisible.value = true
}

// 从详情弹窗点击编辑
const handleEditFromDetail = () => {
  if (currentDetail.value) {
    detailDialogVisible.value = false
    handleConfig(currentDetail.value)
  }
}

// 打开配置弹窗
const handleConfig = async (row: GroupOption & { sync_time?: string }) => {
  currentGroup.value = row

  // 重置表单
  configForm.customer_service_wxid = ''
  configForm.customer_service_name = ''
  configForm.model_suppliers = []
  customerSearchResults.value = []
  currentGroupMembers.value = []  // 清空群成员缓存

  // 先加载群成员列表
  await loadAllGroupMembers()

  // 加载已有配置
  try {
    const config = await groupConfigApi.getDetail(row.group_id)
    if (config) {
      configForm.customer_service_wxid = config.customer_service_wxid || ''
      configForm.customer_service_name = config.customer_service_name || ''
      
      // 为每个供应商绑定设置搜索结果为当前群成员，以便显示昵称
      configForm.model_suppliers = config.model_suppliers.map(ms => ({
        car_model_id: ms.car_model_id,
        supplier_wxid: ms.supplier_wxid || '',
        supplier_name: ms.supplier_name || '',
        supplier_search_results: currentGroupMembers.value,  // 使用已加载的群成员
        loadingMembers: false
      }))
      
      // 设置客服搜索结果为群成员，以便显示昵称
      customerSearchResults.value = currentGroupMembers.value
    }
  } catch (error) {
    // 没有配置也没关系
  }

  configDialogVisible.value = true
}

// 加载群成员列表（缓存起来供搜索使用）
const loadAllGroupMembers = async () => {
  if (!currentGroup.value?.group_id) return
  try {
    // 获取所有群成员（不传入关键词）
    const members = await groupConfigApi.getGroupMembers(
      currentGroup.value.group_id,
      ''
    )
    currentGroupMembers.value = members
    console.log('加载群成员成功:', members)
    return members
  } catch (error) {
    console.error('加载群成员失败', error)
    ElMessage.error('加载群成员失败')
    return []
  }
}

// 加载客服成员列表（点击下拉框时调用）
const loadCustomerMembers = async () => {
  if (!currentGroup.value?.group_id) return
  loadingCustomerMembers.value = true
  try {
    // 如果缓存为空，先加载所有成员
    if (currentGroupMembers.value.length === 0) {
      await loadAllGroupMembers()
    }
    customerSearchResults.value = currentGroupMembers.value
  } catch (error) {
    console.error('加载客服成员失败', error)
    ElMessage.error('加载群成员失败')
  } finally {
    loadingCustomerMembers.value = false
  }
}

// 添加车型供应商绑定
const addModelSupplier = () => {
  configForm.model_suppliers.push({
    car_model_id: null,
    supplier_wxid: '',
    supplier_name: '',
    supplier_search_results: [],
    loadingMembers: false
  })
}

// 移除车型供应商绑定
const removeModelSupplier = (index: number) => {
  configForm.model_suppliers.splice(index, 1)
}

// 加载供应商成员列表（点击下拉框时调用）
const loadSupplierMembers = async (index: number) => {
  if (!currentGroup.value?.group_id) return
  const item = configForm.model_suppliers[index]
  item.loadingMembers = true
  try {
    // 如果缓存为空，先加载所有成员
    if (currentGroupMembers.value.length === 0) {
      await loadAllGroupMembers()
    }
    item.supplier_search_results = currentGroupMembers.value
  } catch (error) {
    console.error('加载供应商成员失败', error)
    ElMessage.error('加载群成员失败')
  } finally {
    item.loadingMembers = false
  }
}

// 保存配置
const saveConfig = async () => {
  if (!currentGroup.value) return

  savingConfig.value = true
  try {
    // 获取客服名称
    const customerMember = customerSearchResults.value.find(
      m => m.wxid === configForm.customer_service_wxid
    )
    const customerName = customerMember
      ? (customerMember.nick || customerMember.group_nick || customerMember.wxid)
      : configForm.customer_service_name

    // 处理供应商绑定
    const modelSuppliers = configForm.model_suppliers
      .filter(item => item.car_model_id && item.supplier_wxid)
      .map(item => {
        const supplierMember = item.supplier_search_results.find(
          m => m.wxid === item.supplier_wxid
        )
        return {
          car_model_id: item.car_model_id,
          supplier_id: 0,
          supplier_wxid: item.supplier_wxid,
          supplier_name: supplierMember
            ? (supplierMember.nick || supplierMember.group_nick || supplierMember.wxid)
            : item.supplier_name
        }
      })

    const data = {
      group_id: currentGroup.value.group_id,
      group_name: currentGroup.value.group_name,
      customer_service_wxid: configForm.customer_service_wxid,
      customer_service_name: customerName,
      model_suppliers: modelSuppliers
    }

    // 判断是创建还是更新 - 先检查是否已有配置
    let existingConfig = null
    try {
      existingConfig = await groupConfigApi.getDetail(currentGroup.value.group_id)
    } catch (err) {
      // 获取详情失败，假设配置不存在
      console.log('获取配置详情失败，假设为新建配置:', err)
      existingConfig = null
    }

    if (existingConfig && existingConfig.id) {
      // 已存在配置，调用更新API
      await groupConfigApi.update(existingConfig.id, {
        group_name: data.group_name,
        customer_service_wxid: data.customer_service_wxid,
        customer_service_name: data.customer_service_name,
        model_suppliers: data.model_suppliers
      })
      ElMessage.success('配置更新成功')
    } else {
      // 不存在配置，调用创建API
      await groupConfigApi.create(data)
      ElMessage.success('配置创建成功')
    }

    configDialogVisible.value = false
    // 刷新列表以更新配置状态
    loadSyncedGroups()
  } catch (error: any) {
    console.error('保存配置失败', error)
    // 显示更详细的错误信息
    const errorMsg = error?.response?.data?.message || error?.message || '保存失败'
    ElMessage.error(`保存失败: ${errorMsg}`)
  } finally {
    savingConfig.value = false
  }
}

const handlePagination = ({ page, limit }: { page: number; limit: number }) => {
  query.page = page
  query.pageSize = limit
}

onMounted(() => {
  loadSyncedGroups()
  loadCarModels()
})
</script>

<style scoped>
/* 与群管理页面保持一致的样式 */
.search-form-container {
  background: var(--bg-white);
  border-radius: var(--border-radius-large);
  padding: var(--spacing-md) var(--spacing-lg);
  margin-bottom: var(--spacing-md);
  box-shadow: var(--shadow-base);
}

.table-operations {
  margin-bottom: var(--spacing-md);
}

:deep(.el-card) {
  border: none;
  box-shadow: var(--shadow-base);
}

/* 配置弹窗样式 */
.config-card {
  padding: 10px;
}

.group-info {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.group-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: var(--text-primary);
}

.config-section {
  margin-bottom: 25px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

.search-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.model-supplier-row {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
}

.supplier-search {
  display: flex;
  align-items: center;
}

.member-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.member-name {
  font-weight: 500;
}

.member-wxid {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

/* 树形选择组件样式 */
:deep(.el-tree-select__popper) {
  min-width: 280px !important;
}

:deep(.el-tree-node__label) {
  font-size: 14px;
  white-space: nowrap;
  overflow: visible;
}

:deep(.el-select-dropdown__item) {
  font-size: 14px;
}

/* 车型下拉树样式 */
:deep(.car-model-tree-dropdown) {
  min-width: 320px !important;
  max-width: 450px;
  max-height: 600px !important;
}

:deep(.car-model-tree-dropdown .el-tree) {
  max-height: 580px !important;
  overflow-y: auto;
}

:deep(.car-model-tree-dropdown .el-tree-node__content) {
  height: 32px;
  line-height: 32px;
}

:deep(.car-model-tree-dropdown .el-tree-node__label) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
}

:deep(.car-model-tree-dropdown .el-select-dropdown__item) {
  padding: 0 16px;
}

/* 确保下拉框内容可滚动 */
:deep(.car-model-tree-dropdown .el-scrollbar__wrap) {
  max-height: 580px !important;
}

:deep(.car-model-tree-dropdown .el-select-dropdown__wrap) {
  max-height: 580px !important;
}

/* 树节点样式 */
:deep(.car-model-tree-dropdown .el-tree-node__children) {
  overflow: visible;
}

/* 客服和供应商下拉框样式 */
:deep(.el-select-dropdown__wrap) {
  max-height: 400px !important;
}

:deep(.el-select-dropdown__list) {
  max-height: 400px;
  overflow-y: auto;
}

:deep(.el-scrollbar__wrap) {
  max-height: 400px !important;
}

/* 详情弹窗样式 */
.detail-card {
  padding: 10px;
}

.detail-section {
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.detail-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h4 {
  margin: 0;
  font-size: 16px;
  color: var(--text-primary);
}

.detail-item {
  display: flex;
  margin-bottom: 10px;
  font-size: 14px;
}

.detail-item .label {
  color: #909399;
  min-width: 100px;
}

.detail-item .value {
  color: var(--text-primary);
  flex: 1;
  word-break: break-all;
}

.supplier-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.supplier-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.supplier-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.supplier-name {
  font-weight: 500;
  color: var(--text-primary);
}

.supplier-wxid {
  font-size: 12px;
  color: #909399;
}
</style>
