<template>
  <div class="page-container">
    <!-- 高级筛选 -->
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
        <el-form-item label="识别状态">
          <el-select v-model="query.status" placeholder="请选择" clearable style="width: 120px">
            <el-option label="成功" value="success" />
            <el-option label="失败" value="fail" />
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
        <el-form-item label="车架号">
          <el-input v-model="query.vin" placeholder="请输入VIN" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="车型">
          <el-input v-model="query.model" placeholder="请输入车型" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="是否报价">
          <el-select v-model="query.isQuoted" placeholder="请选择" clearable style="width: 120px">
            <el-option label="是" :value="true" />
            <el-option label="否" :value="false" />
          </el-select>
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
        <el-table-column prop="date" label="日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.date) }}
          </template>
        </el-table-column>
        <el-table-column prop="recognize_status" label="识别状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.recognize_status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.recognize_status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="vin_code" label="车架号" width="180" />
        <el-table-column prop="car_model" label="车型" show-overflow-tooltip />
        <el-table-column prop="source_group" label="来源群" />
        <el-table-column prop="inquirer" label="询价人" />
        <el-table-column prop="quoter" label="报价人" />
        <el-table-column prop="is_quoted" label="是否报价" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_quoted ? 'success' : 'info'" size="small">
              {{ row.is_quoted ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quote_time" label="报价时效" width="120">
          <template #default="{ row }">
            {{ row.quote_time || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="supplier" label="汽配商" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleDetail(row)">
              <el-icon><View /></el-icon>详情
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
    
    <!-- 详情弹窗 -->
    <el-dialog v-model="detailDialog" title="识别详情" width="700px">
      <el-descriptions :column="2" border v-if="currentRecord">
        <el-descriptions-item label="车架号">{{ currentRecord.vin_code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="车型">{{ currentRecord.car_model || '-' }}</el-descriptions-item>
        <el-descriptions-item label="来源群">{{ currentRecord.source_group || '-' }}</el-descriptions-item>
        <el-descriptions-item label="询价人">{{ currentRecord.inquirer || '-' }}</el-descriptions-item>
        <el-descriptions-item label="识别状态">
          <el-tag :type="currentRecord.recognize_status === 'success' ? 'success' : 'danger'">
            {{ currentRecord.recognize_status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="识别日期">{{ formatDate(currentRecord.date) }}</el-descriptions-item>
        <el-descriptions-item label="报价人">{{ currentRecord.quoter || '-' }}</el-descriptions-item>
        <el-descriptions-item label="是否报价">
          <el-tag :type="currentRecord.is_quoted ? 'success' : 'info'">
            {{ currentRecord.is_quoted ? '是' : '否' }}
          </el-tag>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import Pagination from '@/components/common/Pagination.vue'
import { vinApi } from '@/api/vin'
import { groupApi } from '@/api/group'
import type { VinRecord } from '@/types/vin'

const loading = ref(false)
const tableData = ref<VinRecord[]>([])
const total = ref(0)
const groupOptions = ref<{label: string, value: string}[]>([])
const query = reactive({
  page: 1,
  pageSize: 10,
  dateRange: [] as string[],
  status: undefined as string | undefined,
  sourceGroup: '',
  vin: '',
  model: '',
  isQuoted: undefined as boolean | undefined
})

const detailDialog = ref(false)
const currentRecord = ref<VinRecord | null>(null)

const formatDate = (date: string | Date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN')
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
    
    if (query.status) {
      params.recognize_status = query.status
    }
    
    if (query.sourceGroup) {
      params.source_group = query.sourceGroup
    }
    
    if (query.vin) {
      params.vin_code = query.vin
    }
    
    if (query.model) {
      params.car_model = query.model
    }
    
    if (query.isQuoted !== undefined) {
      params.is_quoted = query.isQuoted
    }
    
    const res = await vinApi.getRecords(params)
    tableData.value = res.list || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取车架号记录失败', error)
    ElMessage.error('获取车架号记录失败')
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
  query.status = undefined
  query.sourceGroup = ''
  query.vin = ''
  query.model = ''
  query.isQuoted = undefined
  query.page = 1
  loadData()
}

const handlePagination = ({ page, limit }: { page: number; limit: number }) => {
  query.page = page
  query.pageSize = limit
  loadData()
}

const handleDetail = async (row: VinRecord) => {
  try {
    const res = await vinApi.getDetail(row.id)
    currentRecord.value = res
    detailDialog.value = true
  } catch (error) {
    ElMessage.error('获取详情失败')
  }
}

const handleDelete = (row: VinRecord) => {
  ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await vinApi.deleteRecord(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

onMounted(() => {
  loadGroupOptions()
  loadData()
})
</script>

<style scoped>
</style>
