<template>
  <div class="page-container">
    <!-- 筛选条件 -->
    <div class="search-form-container">
      <el-form :model="query" inline>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="query.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="消息类型">
          <el-select v-model="query.messageType" placeholder="请选择" clearable style="width: 120px">
            <el-option label="文本" value="text" />
            <el-option label="图片" value="image" />
            <el-option label="语音" value="voice" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源群">
          <el-select v-model="query.sourceGroup" placeholder="请选择" clearable style="width: 150px">
            <el-option 
              v-for="group in groupOptions" 
              :key="group.value" 
              :label="group.label" 
              :value="group.value" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="询价人">
          <el-input v-model="query.inquirer" placeholder="请输入询价人" clearable style="width: 150px" />
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
    
    <!-- 数据表格 -->
    <el-card>
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="msg_type" label="消息类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getMessageTypeTag(row.msg_type)" size="small">
              {{ getMessageTypeLabel(row.msg_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="图片内容" width="100">
          <template #default="{ row }">
            <el-image
              v-if="row.msg_type === 'image' && row.image_content"
              :src="row.image_content"
              :preview-src-list="[row.image_content]"
              fit="cover"
              style="width: 60px; height: 60px; border-radius: 4px"
              preview-teleported
              :initial-index="0"
              :hide-on-click-modal="true"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="msg_date" label="日期" width="160">
          <template #default="{ row }">
            {{ formatDate(row.msg_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="inquirer" label="询价人" />
        <el-table-column prop="vin_code" label="车架号" width="180" />
        <el-table-column prop="car_model" label="车型" show-overflow-tooltip />
        <el-table-column prop="source_group" label="来源群" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleDetail(row)">
              <el-icon><View /></el-icon>详情
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
    
    <!-- 详情弹窗 -->
    <el-dialog v-model="detailDialog" title="消息详情" width="600px">
      <el-descriptions :column="1" border v-if="currentRecord">
        <el-descriptions-item label="消息类型">
          <el-tag :type="getMessageTypeTag(currentRecord.msg_type)">
            {{ getMessageTypeLabel(currentRecord.msg_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="日期">{{ formatDate(currentRecord.msg_date) }}</el-descriptions-item>
        <el-descriptions-item label="询价人">{{ currentRecord.inquirer || '-' }}</el-descriptions-item>
        <el-descriptions-item label="车架号">{{ currentRecord.vin_code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="车型">{{ currentRecord.car_model || '-' }}</el-descriptions-item>
        <el-descriptions-item label="来源群">{{ currentRecord.source_group || '-' }}</el-descriptions-item>
        <el-descriptions-item label="原始消息" v-if="currentRecord.raw_message">
          <pre style="white-space: pre-wrap; word-break: break-all;">{{ currentRecord.raw_message }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="图片" v-if="currentRecord.msg_type === 'image' && currentRecord.image_content">
          <el-image
            :src="currentRecord.image_content"
            :preview-src-list="[currentRecord.image_content]"
            fit="contain"
            style="max-width: 100%; max-height: 300px"
            preview-teleported
            :initial-index="0"
            :hide-on-click-modal="true"
          />
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import Pagination from '@/components/common/Pagination.vue'
import { statisticsApi } from '@/api/statistics'
import { groupApi } from '@/api/group'
import type { MessageRecord } from '@/api/statistics'

const loading = ref(false)
const tableData = ref<MessageRecord[]>([])
const total = ref(0)
const groupOptions = ref<{label: string, value: string}[]>([])
const query = reactive({
  page: 1,
  pageSize: 10,
  dateRange: [] as string[],
  messageType: '',
  sourceGroup: '',
  inquirer: ''
})

const detailDialog = ref(false)
const currentRecord = ref<MessageRecord | null>(null)

const getMessageTypeTag = (type: string) => {
  const map: Record<string, string> = {
    text: '',
    image: 'success',
    voice: 'warning'
  }
  return map[type] || ''
}

const getMessageTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    text: '文本',
    image: '图片',
    voice: '语音'
  }
  return map[type] || type
}

const formatDate = (date: string | Date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 加载群聊选项
const loadGroupOptions = async () => {
  try {
    const res = await groupApi.getList({ page: 1, pageSize: 100 })
    if (res.list) {
      groupOptions.value = res.list.map((group: any) => ({
        label: group.group_name,
        value: group.group_id
      }))
    }
  } catch (error) {
    console.error('加载群聊列表失败', error)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params: any = {
      page: query.page,
      page_size: query.pageSize
    }
    
    if (query.dateRange && query.dateRange.length === 2) {
      params.start_date = query.dateRange[0]
      params.end_date = query.dateRange[1]
    }
    
    if (query.messageType) {
      params.msg_type = query.messageType
    }
    
    if (query.sourceGroup) {
      params.source_group = query.sourceGroup
    }
    
    if (query.inquirer) {
      params.inquirer = query.inquirer
    }
    
    const res = await statisticsApi.getMessageRecords(params)
    tableData.value = res.list || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取消息记录失败', error)
    ElMessage.error('获取消息记录失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  query.page = 1
  loadData()
}

const handleReset = () => {
  query.dateRange = []
  query.messageType = ''
  query.sourceGroup = ''
  query.inquirer = ''
  query.page = 1
  loadData()
}

const handlePagination = ({ page, limit }: { page: number; limit: number }) => {
  query.page = page
  query.pageSize = limit
  loadData()
}

const handleDetail = (row: MessageRecord) => {
  currentRecord.value = row
  detailDialog.value = true
}

onMounted(() => {
  loadGroupOptions()
  loadData()
})
</script>
