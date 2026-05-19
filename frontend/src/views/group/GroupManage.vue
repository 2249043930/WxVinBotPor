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
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>添加群
      </el-button>
      <el-button type="success" @click="handleSync" :loading="syncLoading">
        <el-icon><Refresh /></el-icon>自动获取微信群
      </el-button>
    </div>
    
    <!-- 数据表格 -->
    <el-card>
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="group_name" label="群名称" />
        <el-table-column prop="group_id" label="群ID" />
        <el-table-column prop="member_count" label="成员数" width="100" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              :active-value="true"
              :inactive-value="false"
              @change="(val) => handleStatusChange(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button type="primary" link @click="handleNotification(row)">
              <el-icon><Bell /></el-icon>通知配置
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <Pagination
        :total="total"
        :page="query.page"
        :limit="query.pageSize"
        @pagination="handlePagination"
      />
    </el-card>
    
    <!-- 添加/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="群名称">
          <el-input v-model="form.name" placeholder="请输入群名称" />
        </el-form-item>
        <el-form-item label="群ID">
          <el-input v-model="form.groupId" placeholder="请输入群ID" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 通知配置弹窗 -->
    <el-dialog v-model="notificationDialog" title="通知配置" width="600px">
      <el-form :model="notificationForm" label-width="120px">
        <el-form-item label="询价通知">
          <el-switch v-model="notificationForm.inquiry" />
        </el-form-item>
        <el-form-item label="报价通知">
          <el-switch v-model="notificationForm.quote" />
        </el-form-item>
        <el-form-item label="发货通知">
          <el-switch v-model="notificationForm.shipping" />
        </el-form-item>
        <el-form-item label="成交通知">
          <el-switch v-model="notificationForm.deal" />
        </el-form-item>
        <el-form-item label="工作时间">
          <el-time-picker
            v-model="notificationForm.workTimeStart"
            placeholder="开始时间"
            format="HH:mm"
            style="width: 140px"
          />
          <span style="margin: 0 10px;">至</span>
          <el-time-picker
            v-model="notificationForm.workTimeEnd"
            placeholder="结束时间"
            format="HH:mm"
            style="width: 140px"
          />
        </el-form-item>

        <!-- 关键词配置 -->
        <el-divider>关键词配置</el-divider>

        <el-form-item label="报价关键词">
          <div class="keywords-input">
            <el-tag
              v-for="(tag, index) in notificationForm.quoteKeywords"
              :key="index"
              closable
              @close="removeKeyword('quote', index)"
              style="margin-right: 8px; margin-bottom: 8px;"
            >
              {{ tag }}
            </el-tag>
            <el-input
              v-if="quoteInputVisible"
              ref="quoteInputRef"
              v-model="quoteInputValue"
              size="small"
              style="width: 100px;"
              @keyup.enter="handleKeywordConfirm('quote')"
              @blur="handleKeywordConfirm('quote')"
            />
            <el-button v-else size="small" @click="showKeywordInput('quote')">
              + 添加
            </el-button>
          </div>
          <div class="form-tip">检测到这些关键词时触发报价通知</div>
        </el-form-item>

        <el-form-item label="发货关键词">
          <div class="keywords-input">
            <el-tag
              v-for="(tag, index) in notificationForm.deliveryKeywords"
              :key="index"
              closable
              @close="removeKeyword('delivery', index)"
              style="margin-right: 8px; margin-bottom: 8px;"
            >
              {{ tag }}
            </el-tag>
            <el-input
              v-if="deliveryInputVisible"
              ref="deliveryInputRef"
              v-model="deliveryInputValue"
              size="small"
              style="width: 100px;"
              @keyup.enter="handleKeywordConfirm('delivery')"
              @blur="handleKeywordConfirm('delivery')"
            />
            <el-button v-else size="small" @click="showKeywordInput('delivery')">
              + 添加
            </el-button>
          </div>
          <div class="form-tip">检测到这些关键词时触发发货通知</div>
        </el-form-item>

        <el-form-item label="成交关键词">
          <div class="keywords-input">
            <el-tag
              v-for="(tag, index) in notificationForm.dealKeywords"
              :key="index"
              closable
              @close="removeKeyword('deal', index)"
              style="margin-right: 8px; margin-bottom: 8px;"
            >
              {{ tag }}
            </el-tag>
            <el-input
              v-if="dealInputVisible"
              ref="dealInputRef"
              v-model="dealInputValue"
              size="small"
              style="width: 100px;"
              @keyup.enter="handleKeywordConfirm('deal')"
              @blur="handleKeywordConfirm('deal')"
            />
            <el-button v-else size="small" @click="showKeywordInput('deal')">
              + 添加
            </el-button>
          </div>
          <div class="form-tip">检测到这些关键词时触发成交通知</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="notificationDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmNotification">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Pagination from '@/components/common/Pagination.vue'
import { groupApi } from '@/api/group'
import { formatDate } from '@/utils/format'
import type { Group, GroupForm, GroupNotification } from '@/types/group'

const loading = ref(false)
const syncLoading = ref(false)
const tableData = ref<Group[]>([])
const total = ref(0)
const query = reactive({
  page: 1,
  pageSize: 10,
  keyword: ''
})

const dialogVisible = ref(false)
const dialogTitle = ref('添加群')
const form = reactive<GroupForm>({
  name: '',
  groupId: '',
  status: 1
})

const notificationDialog = ref(false)
const currentGroup = ref<Group | null>(null)

// 将时间字符串转换为 Date 对象
const timeStringToDate = (timeStr: string): Date => {
  const [hours, minutes] = timeStr.split(':').map(Number)
  const date = new Date()
  date.setHours(hours, minutes, 0, 0)
  return date
}

// 将 Date 对象转换为时间字符串
const dateToTimeString = (date: Date): string => {
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const notificationForm = reactive({
  inquiry: true,
  quote: true,
  shipping: false,
  deal: true,
  workTimeStart: timeStringToDate('09:00'),
  workTimeEnd: timeStringToDate('18:00'),
  quoteKeywords: [] as string[],
  deliveryKeywords: [] as string[],
  dealKeywords: [] as string[]
})

// 关键词输入相关
const quoteInputVisible = ref(false)
const quoteInputValue = ref('')
const quoteInputRef = ref<HTMLInputElement>()

const deliveryInputVisible = ref(false)
const deliveryInputValue = ref('')
const deliveryInputRef = ref<HTMLInputElement>()

const dealInputVisible = ref(false)
const dealInputValue = ref('')
const dealInputRef = ref<HTMLInputElement>()

// 显示关键词输入框
const showKeywordInput = (type: 'quote' | 'delivery' | 'deal') => {
  if (type === 'quote') {
    quoteInputVisible.value = true
    nextTick(() => {
      quoteInputRef.value?.focus()
    })
  } else if (type === 'delivery') {
    deliveryInputVisible.value = true
    nextTick(() => {
      deliveryInputRef.value?.focus()
    })
  } else if (type === 'deal') {
    dealInputVisible.value = true
    nextTick(() => {
      dealInputRef.value?.focus()
    })
  }
}

// 确认添加关键词
const handleKeywordConfirm = (type: 'quote' | 'delivery' | 'deal') => {
  if (type === 'quote') {
    const value = quoteInputValue.value.trim()
    if (value && !notificationForm.quoteKeywords.includes(value)) {
      notificationForm.quoteKeywords.push(value)
    }
    quoteInputVisible.value = false
    quoteInputValue.value = ''
  } else if (type === 'delivery') {
    const value = deliveryInputValue.value.trim()
    if (value && !notificationForm.deliveryKeywords.includes(value)) {
      notificationForm.deliveryKeywords.push(value)
    }
    deliveryInputVisible.value = false
    deliveryInputValue.value = ''
  } else if (type === 'deal') {
    const value = dealInputValue.value.trim()
    if (value && !notificationForm.dealKeywords.includes(value)) {
      notificationForm.dealKeywords.push(value)
    }
    dealInputVisible.value = false
    dealInputValue.value = ''
  }
}

// 移除关键词
const removeKeyword = (type: 'quote' | 'delivery' | 'deal', index: number) => {
  if (type === 'quote') {
    notificationForm.quoteKeywords.splice(index, 1)
  } else if (type === 'delivery') {
    notificationForm.deliveryKeywords.splice(index, 1)
  } else if (type === 'deal') {
    notificationForm.dealKeywords.splice(index, 1)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await groupApi.getList({
      page: query.page,
      pageSize: query.pageSize,
      keyword: query.keyword
    })
    // request.ts 拦截器已经处理了响应，直接返回 data
    tableData.value = res.list || []
    total.value = res.total || 0
  } catch (error) {
    ElMessage.error('获取群列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  query.page = 1
  loadData()
}

const handleReset = () => {
  query.keyword = ''
  query.page = 1
  loadData()
}

const handlePagination = ({ page, limit }: { page: number; limit: number }) => {
  query.page = page
  query.pageSize = limit
  loadData()
}

const handleAdd = () => {
  dialogTitle.value = '添加群'
  form.id = undefined
  form.name = ''
  form.groupId = ''
  form.status = 1
  dialogVisible.value = true
}

const handleEdit = (row: Group) => {
  dialogTitle.value = '编辑群'
  form.id = row.id
  form.name = row.group_name
  form.groupId = row.group_id
  form.status = row.is_active ? 1 : 0
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    if (!form.name || !form.groupId) {
      ElMessage.warning('请填写完整的群信息')
      return
    }
    
    const data = {
      name: form.name,
      groupId: form.groupId,
      status: form.status
    }
    
    if (form.id) {
      await groupApi.update(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await groupApi.create(data)
      ElMessage.success('添加成功')
    }
    
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error(form.id ? '更新失败' : '添加失败')
  }
}

const handleDelete = async (row: Group) => {
  try {
    await ElMessageBox.confirm(`确定要删除群"${row.name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await groupApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleStatusChange = async (row: Group, val: number) => {
  try {
    await groupApi.toggleStatus(row.id, val)
    ElMessage.success('状态更新成功')
  } catch (error) {
    row.status = val === 1 ? 0 : 1
  }
}

const handleNotification = async (row: Group) => {
  currentGroup.value = row
  try {
    // 加载当前群的通知配置
    const config = await groupApi.getNotification(row.id)
    notificationForm.inquiry = config.inquiry_notify ?? true
    notificationForm.quote = config.quote_notify ?? true
    notificationForm.shipping = config.delivery_notify ?? false
    notificationForm.deal = config.deal_notify ?? true
    notificationForm.workTimeStart = timeStringToDate(config.work_start_time || '09:00')
    notificationForm.workTimeEnd = timeStringToDate(config.work_end_time || '18:00')

    // 加载关键词配置
    const keywordsConfig = config.keywords_config || {}
    notificationForm.quoteKeywords = keywordsConfig.quote_keywords || []
    notificationForm.deliveryKeywords = keywordsConfig.delivery_keywords || []
    notificationForm.dealKeywords = keywordsConfig.deal_keywords || []
  } catch (error) {
    // 如果获取失败，使用默认值
    notificationForm.inquiry = true
    notificationForm.quote = true
    notificationForm.shipping = false
    notificationForm.deal = true
    notificationForm.workTimeStart = timeStringToDate('09:00')
    notificationForm.workTimeEnd = timeStringToDate('18:00')
    notificationForm.quoteKeywords = []
    notificationForm.deliveryKeywords = []
    notificationForm.dealKeywords = []
  }
  notificationDialog.value = true
}

const confirmNotification = async () => {
  if (!currentGroup.value) return

  try {
    await groupApi.updateNotification(currentGroup.value.id, {
      inquiry_notify: notificationForm.inquiry,
      quote_notify: notificationForm.quote,
      delivery_notify: notificationForm.shipping,
      deal_notify: notificationForm.deal,
      work_start_time: dateToTimeString(notificationForm.workTimeStart),
      work_end_time: dateToTimeString(notificationForm.workTimeEnd),
      keywords_config: {
        quote_keywords: notificationForm.quoteKeywords,
        delivery_keywords: notificationForm.deliveryKeywords,
        deal_keywords: notificationForm.dealKeywords
      }
    })
    ElMessage.success('通知配置保存成功')
    notificationDialog.value = false
  } catch (error) {
    ElMessage.error('保存通知配置失败')
  }
}

const handleSync = async () => {
  try {
    syncLoading.value = true
    const res = await groupApi.syncGroups()
    // 拦截器已经处理了响应，成功时直接返回 data
    ElMessage.success(`成功同步 ${res.synced_count} 个群聊`)
    loadData()
  } catch (error: any) {
    // 拦截器会在 code !== 0 时抛出错误
    ElMessage.error(error.message || '同步微信群失败')
  } finally {
    syncLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.keywords-input {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
