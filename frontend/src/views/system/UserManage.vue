<template>
  <div class="page-container">
    <!-- 搜索栏 -->
    <SearchForm
      :fields="searchFields"
      @search="handleSearch"
      @reset="handleReset"
    />
    
    <!-- 操作栏 -->
    <div class="table-operations">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>添加用户
      </el-button>
    </div>
    
    <!-- 数据表格 -->
    <el-card>
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="nickname" label="用户昵称" />
        <el-table-column prop="username" label="登录账号" />
        <el-table-column prop="phone" label="手机号码" />
        <el-table-column prop="email" label="邮箱账号" show-overflow-tooltip />
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        <el-table-column prop="createTime" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.createTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="(val) => handleStatusChange(row, val)"
              :loading="row.statusLoading"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button type="primary" link @click="handleResetPwd(row)">
              <el-icon><Key /></el-icon>重置密码
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <Pagination
        :total="total"
        :page="query.page"
        :limit="query.pageSize"
        @pagination="handlePagination"
      />
    </el-card>
    
    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="请输入用户昵称" />
        </el-form-item>
        <el-form-item label="登录账号" prop="username">
          <el-input v-model="form.username" placeholder="请输入登录账号" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="用户密码" prop="password" v-if="!form.id">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号码" />
        </el-form-item>
        <el-form-item label="邮箱账号" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱账号" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import SearchForm from '@/components/common/SearchForm.vue'
import Pagination from '@/components/common/Pagination.vue'
import { userApi } from '@/api/user'
import { formatDate } from '@/utils/format'
import { isPhone, isEmail, isUsername, isPassword } from '@/utils/validate'
import type { User, UserForm } from '@/types/user'

const loading = ref(false)
const tableData = ref<User[]>([])
const total = ref(0)
const query = reactive({
  page: 1,
  pageSize: 10,
  keyword: ''
})

const searchFields = [
  { prop: 'keyword', label: '', type: 'input', placeholder: '请输入用户名/昵称' }
]

const dialogVisible = ref(false)
const dialogTitle = ref('添加用户')
const submitting = ref(false)
const formRef = ref<FormInstance>()
const form = reactive<UserForm>({
  nickname: '',
  username: '',
  password: '',
  phone: '',
  email: '',
  remark: ''
})

const formRules: FormRules = {
  nickname: [
    { required: true, message: '请输入用户昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度2-20个字符', trigger: 'blur' }
  ],
  username: [
    { required: true, message: '请输入登录账号', trigger: 'blur' },
    { validator: (rule, value, callback) => {
      if (!isUsername(value)) {
        callback(new Error('4-20位字母数字下划线'))
      } else {
        callback()
      }
    }, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { validator: (rule, value, callback) => {
      if (!isPassword(value)) {
        callback(new Error('6-20位字符'))
      } else {
        callback()
      }
    }, trigger: 'blur' }
  ],
  phone: [
    { validator: (rule, value, callback) => {
      if (value && !isPhone(value)) {
        callback(new Error('手机号格式错误'))
      } else {
        callback()
      }
    }, trigger: 'blur' }
  ],
  email: [
    { validator: (rule, value, callback) => {
      if (value && !isEmail(value)) {
        callback(new Error('邮箱格式错误'))
      } else {
        callback()
      }
    }, trigger: 'blur' }
  ]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await userApi.getList(query)
    // 将后端的 is_active 布尔值映射为前端的 status 数字
    tableData.value = res.list.map((user: any) => ({
      ...user,
      status: user.is_active ? 1 : 0,
      statusLoading: false
    }))
    total.value = res.total
  } catch (error) {
    console.error('获取用户列表失败', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = (data: any) => {
  query.keyword = data.keyword
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
  dialogTitle.value = '添加用户'
  form.id = undefined
  form.nickname = ''
  form.username = ''
  form.password = ''
  form.phone = ''
  form.email = ''
  form.remark = ''
  dialogVisible.value = true
}

const handleEdit = (row: User) => {
  dialogTitle.value = '编辑用户'
  form.id = row.id
  form.nickname = row.nickname
  form.username = row.username
  form.password = ''
  form.phone = row.phone || ''
  form.email = row.email || ''
  form.remark = row.remark || ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (form.id) {
        await userApi.update(form.id, form)
        ElMessage.success('更新成功')
      } else {
        await userApi.create(form)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadData()
    } catch (error) {
      console.error('保存失败', error)
    } finally {
      submitting.value = false
    }
  })
}

const handleDelete = (row: User) => {
  ElMessageBox.confirm(`确定要删除用户"${row.nickname}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await userApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  })
}

const handleResetPwd = (row: User) => {
  ElMessageBox.confirm(`确定要重置"${row.nickname}"的密码吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await userApi.resetPassword(row.id)
    ElMessage.success('密码重置成功，新密码已发送至用户邮箱')
  })
}

const handleStatusChange = async (row: any, val: number) => {
  // 防止重复提交
  if (row.statusLoading) return
  
  row.statusLoading = true
  try {
    await userApi.toggleStatus(row.id, val)
    ElMessage.success('状态更新成功')
  } catch (error) {
    // 恢复原状态
    row.status = val === 1 ? 0 : 1
    ElMessage.error('状态更新失败')
  } finally {
    row.statusLoading = false
  }
}

onMounted(() => {
  loadData()
})
</script>
