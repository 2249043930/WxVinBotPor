<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>接口配置</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>添加配置
          </el-button>
        </div>
      </template>

      <!-- 配置类型标签页 -->
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="LLM配置" name="llm" />
        <el-tab-pane label="VIN接口" name="vin" />
        <el-tab-pane label="数据库" name="database" />
        <el-tab-pane label="千寻微信" name="qianxun" />
      </el-tabs>

      <!-- 数据表格 -->
      <el-table :data="tableData" stripe v-loading="loading" style="margin-top: 20px">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="name" label="配置名称" />
        <el-table-column prop="model" label="模型/API" v-if="activeTab === 'llm'" />
        <el-table-column prop="api_base" label="API地址" show-overflow-tooltip />
        <el-table-column label="默认" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="success">默认</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.is_active" @change="(val) => handleStatusChange(row, val)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入配置名称" />
        </el-form-item>

        <!-- LLM特有字段 -->
        <template v-if="activeTab === 'llm'">
          <el-form-item label="API Key" prop="api_key">
            <el-input v-model="form.api_key" type="password" show-password placeholder="请输入API Key" />
          </el-form-item>
          <el-form-item label="API地址" prop="api_base">
            <el-input v-model="form.api_base" placeholder="如：https://api.moonshot.cn/v1" />
          </el-form-item>
          <el-form-item label="模型名称" prop="model">
            <el-input v-model="form.model" placeholder="如：moonshot-v1-8k-vision-preview" />
          </el-form-item>
          <el-form-item label="温度参数">
            <el-slider v-model="form.temperature" :min="0" :max="1" :step="0.1" />
          </el-form-item>
          <el-form-item label="最大Token">
            <el-input-number v-model="form.max_tokens" :min="100" :max="8000" />
          </el-form-item>
          <el-form-item label="提示词模板">
            <el-input v-model="form.prompt_template" type="textarea" :rows="6" placeholder="请输入提示词模板" />
          </el-form-item>
        </template>

        <!-- VIN特有字段 -->
        <template v-if="activeTab === 'vin'">
          <el-form-item label="API Key" prop="api_key">
            <el-input v-model="form.api_key" placeholder="请输入API Key" />
          </el-form-item>
          <el-form-item label="API地址" prop="api_base">
            <el-input v-model="form.api_base" placeholder="请输入API地址" />
          </el-form-item>
        </template>

        <!-- 数据库特有字段 -->
        <template v-if="activeTab === 'database'">
          <el-form-item label="主机" prop="db_host">
            <el-input v-model="form.db_host" placeholder="如：localhost" />
          </el-form-item>
          <el-form-item label="端口" prop="db_port">
            <el-input-number v-model="form.db_port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="数据库名" prop="db_name">
            <el-input v-model="form.db_name" placeholder="请输入数据库名称" />
          </el-form-item>
          <el-form-item label="用户名" prop="db_user">
            <el-input v-model="form.db_user" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码" prop="db_password">
            <el-input v-model="form.db_password" type="password" show-password placeholder="请输入密码" />
          </el-form-item>
        </template>

        <!-- 千寻微信特有字段 -->
        <template v-if="activeTab === 'qianxun'">
          <el-form-item label="微信ID" prop="wx_id">
            <el-input v-model="form.wx_id" placeholder="请输入微信ID" />
          </el-form-item>
          <el-form-item label="API地址" prop="api_url">
            <el-input v-model="form.api_url" placeholder="如：http://127.0.0.1:7777" />
          </el-form-item>
        </template>

        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入描述" />
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
import { apiConfigApi, type ApiConfig } from '@/api/apiConfig'

const activeTab = ref('llm')
const loading = ref(false)
const tableData = ref<ApiConfig[]>([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加配置')
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = reactive<ApiConfig>({
  config_type: 'llm',
  name: '',
  api_key: '',
  api_base: '',
  model: '',
  temperature: '0.1',
  max_tokens: 2000,
  prompt_template: '',
  is_active: true,
  is_default: false,
  description: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  api_key: [{ required: activeTab.value !== 'database' && activeTab.value !== 'qianxun', message: '请输入API Key', trigger: 'blur' }],
  api_base: [{ required: activeTab.value === 'llm' || activeTab.value === 'vin', message: '请输入API地址', trigger: 'blur' }],
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await apiConfigApi.getList(activeTab.value)
    tableData.value = res.list || []
  } catch (error) {
    ElMessage.error('获取配置列表失败')
  } finally {
    loading.value = false
  }
}

const handleTabChange = () => {
  loadData()
}

const handleAdd = () => {
  dialogTitle.value = '添加配置'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: ApiConfig) => {
  dialogTitle.value = '编辑配置'
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = async (row: ApiConfig) => {
  if (!row.id) return
  try {
    await ElMessageBox.confirm(`确定要删除配置"${row.name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await apiConfigApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleStatusChange = async (row: ApiConfig, val: boolean) => {
  if (!row.id) return
  try {
    await apiConfigApi.update(row.id, { is_active: val })
    ElMessage.success('状态更新成功')
  } catch (error) {
    row.is_active = !val
    ElMessage.error('状态更新失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      form.config_type = activeTab.value
      
      // 转换 temperature 为字符串
      const submitData = { ...form }
      if (typeof submitData.temperature === 'number') {
        submitData.temperature = String(submitData.temperature)
      }
      
      if (form.id) {
        // 更新
        await apiConfigApi.update(form.id, submitData)
        ElMessage.success('更新成功')
      } else {
        // 创建
        await apiConfigApi.create(submitData)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      loadData()
    } catch (error) {
      ElMessage.error(form.id ? '更新失败' : '添加失败')
    } finally {
      submitting.value = false
    }
  })
}

const resetForm = () => {
  form.id = undefined
  form.name = ''
  form.api_key = ''
  form.api_base = ''
  form.model = ''
  form.temperature = '0.1'
  form.max_tokens = 2000
  form.prompt_template = ''
  form.db_host = ''
  form.db_port = undefined
  form.db_name = ''
  form.db_user = ''
  form.db_password = ''
  form.wx_id = ''
  form.api_url = ''
  form.is_active = true
  form.is_default = false
  form.description = ''
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
