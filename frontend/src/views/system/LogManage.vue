<template>
  <div class="page-container">
    <!-- 搜索栏 -->
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
        <el-form-item label="用户">
          <el-select v-model="query.userId" placeholder="请选择用户" clearable>
            <el-option
              v-for="user in userOptions"
              :key="user.value"
              :label="user.label"
              :value="user.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="IP地址">
          <el-input v-model="query.ip" placeholder="请输入IP地址" clearable />
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="query.operationType" placeholder="请选择" clearable>
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
            <el-option label="新增" value="create" />
            <el-option label="修改" value="update" />
            <el-option label="删除" value="delete" />
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
        <el-table-column prop="nickname" label="用户昵称" />
        <el-table-column prop="ip_address" label="IP地址" />
        <el-table-column prop="login_location" label="登录地点" />
        <el-table-column prop="os" label="操作系统" />
        <el-table-column prop="browser" label="浏览器" />
        <el-table-column prop="login_time" label="登录时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.login_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="operation" label="操作内容" show-overflow-tooltip />
      </el-table>
      
      <!-- 分页 -->
      <Pagination
        :total="total"
        :page="query.page"
        :limit="query.pageSize"
        @pagination="handlePagination"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import Pagination from '@/components/common/Pagination.vue'
import { logApi } from '@/api/log'
import { userApi } from '@/api/user'
import { formatDate } from '@/utils/format'
import type { LogRecord } from '@/api/log'
import type { SelectOption } from '@/types/common'

const loading = ref(false)
const tableData = ref<LogRecord[]>([])
const total = ref(0)
const userOptions = ref<SelectOption[]>([])

const query = reactive({
  page: 1,
  pageSize: 10,
  dateRange: [] as string[],
  userId: undefined as number | undefined,
  ip: '',
  operationType: ''
})

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      ...query,
      dateRange: query.dateRange?.length === 2 ? query.dateRange : undefined
    }
    const res = await logApi.getList(params)
    tableData.value = res.list
    total.value = res.total
  } catch (error) {
    console.error('获取日志列表失败', error)
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  try {
    const res = await userApi.getList({ page: 1, pageSize: 100 })
    userOptions.value = res.list.map(user => ({
      label: user.nickname,
      value: user.id
    }))
  } catch (error) {
    console.error('获取用户列表失败', error)
  }
}

const handleSearch = () => {
  query.page = 1
  loadData()
}

const handleReset = () => {
  query.dateRange = []
  query.userId = undefined
  query.ip = ''
  query.operationType = ''
  query.page = 1
  loadData()
}

const handlePagination = ({ page, limit }: { page: number; limit: number }) => {
  query.page = page
  query.pageSize = limit
  loadData()
}

onMounted(() => {
  loadData()
  loadUsers()
})
</script>
