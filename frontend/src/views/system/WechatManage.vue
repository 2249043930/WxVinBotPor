<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>微信账号管理</span>
          <el-button type="primary" @click="handleBind">
            <el-icon><Plus /></el-icon>绑定新账号
          </el-button>
        </div>
      </template>
      
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="wxid" label="Wx_id号" />
        <el-table-column prop="nickname" label="微信昵称" />
        <el-table-column prop="avatar" label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :size="40" :src="row.avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '已绑定' : '已解绑' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="bind_time" label="绑定时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.bind_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleRefresh(row)">
              <el-icon><Refresh /></el-icon>刷新
            </el-button>
            <el-button type="danger" link @click="handleUnbind(row)">
              <el-icon><Link /></el-icon>解绑
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
    
    <!-- 绑定弹窗 -->
    <el-dialog v-model="dialogVisible" title="绑定微信账号" width="400px">
      <el-form :model="bindForm" label-width="100px">
        <el-form-item label="Wx_id">
          <el-input v-model="bindForm.wxid" placeholder="请输入Wx_id" />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="bindForm.nickname" placeholder="请输入昵称（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBind" :loading="binding">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Pagination from '@/components/common/Pagination.vue'
import { formatDate } from '@/utils/format'
import { http } from '@/utils/request'

interface WechatAccount {
  id: number
  wxid: string
  nickname: string
  avatar: string
  status: number
  bind_time: string
}

const loading = ref(false)
const tableData = ref<WechatAccount[]>([])
const total = ref(0)
const query = reactive({
  page: 1,
  pageSize: 10
})

const dialogVisible = ref(false)
const binding = ref(false)
const bindForm = reactive({
  wxid: '',
  nickname: ''
})

// 获取微信账号列表
const loadData = async () => {
  loading.value = true
  try {
    const data = await http.get('/v1/wechat/list', {
      params: {
        page: query.page,
        page_size: query.pageSize
      }
    })
    
    tableData.value = data.list || []
    total.value = data.total || 0
  } catch (error) {
    ElMessage.error('获取列表失败')
  } finally {
    loading.value = false
  }
}

const handlePagination = ({ page, limit }: { page: number; limit: number }) => {
  query.page = page
  query.pageSize = limit
  loadData()
}

const handleBind = () => {
  bindForm.wxid = ''
  bindForm.nickname = ''
  dialogVisible.value = true
}

// 绑定微信账号
const confirmBind = async () => {
  if (!bindForm.wxid) {
    ElMessage.warning('请输入Wx_id')
    return
  }

  binding.value = true
  try {
    await http.post('/v1/wechat/bind', {
      wxid: bindForm.wxid,
      nickname: bindForm.nickname
    })

    ElMessage.success('绑定成功')
    dialogVisible.value = false
    loadData()
  } catch (error: any) {
    ElMessage.error(error?.message || '绑定失败')
  } finally {
    binding.value = false
  }
}

// 刷新微信账号信息
const handleRefresh = async (row: WechatAccount) => {
  try {
    await http.post(`/v1/wechat/refresh/${row.id}`)

    ElMessage.success('刷新成功')
    loadData()
  } catch (error: any) {
    ElMessage.error(error?.message || '刷新失败')
  }
}

// 解绑微信账号
const handleUnbind = (row: WechatAccount) => {
  ElMessageBox.confirm(`确定要解绑微信账号"${row.nickname}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await http.post(`/v1/wechat/unbind/${row.id}`)

      ElMessage.success('解绑成功')
      loadData()
    } catch (error: any) {
      ElMessage.error(error?.message || '解绑失败')
    }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
