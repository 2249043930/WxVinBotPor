<template>
  <div class="page-container">
    <!-- 搜索栏 -->
    <div class="search-form-container">
      <el-form :model="query" inline>
        <el-form-item>
          <el-input
            v-model="query.keyword"
            placeholder="搜索车型名称/品牌"
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
        <el-icon><Plus /></el-icon>新增车型
      </el-button>
    </div>

    <!-- 数据表格 -->
    <el-card>
      <el-table :data="carModelList" stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="name" label="车型名称" show-overflow-tooltip />
        <el-table-column prop="brand" label="品牌" show-overflow-tooltip />
        <el-table-column prop="series" label="车系" show-overflow-tooltip />
        <el-table-column prop="displacement" label="排量" width="100" />
        <el-table-column prop="year" label="年份" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>编辑
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

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="车型名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入车型名称" />
        </el-form-item>
        <el-form-item label="品牌" prop="brand">
          <el-input v-model="form.brand" placeholder="请输入品牌，如：宝马、奔驰" />
        </el-form-item>
        <el-form-item label="车系" prop="series">
          <el-input v-model="form.series" placeholder="请输入车系，如：3系、C级" />
        </el-form-item>
        <el-form-item label="排量" prop="displacement">
          <el-input v-model="form.displacement" placeholder="请输入排量，如：2.0T" />
        </el-form-item>
        <el-form-item label="年份" prop="year">
          <el-input v-model="form.year" placeholder="请输入年份，如：2023" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { carModelApi } from '@/api/carModel'
import Pagination from '@/components/common/Pagination.vue'

// 查询参数
const query = reactive({
  keyword: '',
  page: 1,
  pageSize: 10
})

// 表格数据
const loading = ref(false)
const carModelList = ref<any[]>([])
const total = ref(0)

// 弹窗
const dialogVisible = ref(false)
const dialogTitle = ref('新增车型')
const formRef = ref<FormInstance>()
const submitting = ref(false)
const isEdit = ref(false)
const currentId = ref<number | null>(null)

// 表单
const form = reactive({
  name: '',
  brand: '',
  series: '',
  displacement: '',
  year: ''
})

// 表单校验规则
const rules: FormRules = {
  name: [{ required: true, message: '请输入车型名称', trigger: 'blur' }],
  brand: [{ required: true, message: '请输入品牌', trigger: 'blur' }]
}

// 获取车型列表
const loadCarModelList = async () => {
  loading.value = true
  try {
    const data = await carModelApi.getCarModelTree()
    // 拦截器返回的是 res.data，直接是数组
    if (Array.isArray(data)) {
      // 将树形结构扁平化
      const list: any[] = []
      data.forEach((brand: any) => {
        if (brand.children && Array.isArray(brand.children)) {
          brand.children.forEach((model: any) => {
            list.push({
              id: model.id,
              name: model.name,
              brand: model.brand || brand.name,
              series: model.series || '-',
              displacement: model.displacement || '-',
              year: model.year || '-'
            })
          })
        }
      })
      // 本地搜索过滤
      let filtered = list
      if (query.keyword) {
        const keyword = query.keyword.toLowerCase()
        filtered = list.filter(item =>
          item.name.toLowerCase().includes(keyword) ||
          (item.brand && item.brand.toLowerCase().includes(keyword))
        )
      }
      // 分页
      total.value = filtered.length
      const start = (query.page - 1) * query.pageSize
      const end = start + query.pageSize
      carModelList.value = filtered.slice(start, end)
    }
  } catch (error) {
    console.error('加载车型列表失败', error)
    ElMessage.error('加载车型列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  query.page = 1
  loadCarModelList()
}

// 重置
const handleReset = () => {
  query.keyword = ''
  query.page = 1
  loadCarModelList()
}

// 分页
const handlePagination = ({ page, limit }: { page: number; limit: number }) => {
  query.page = page
  query.pageSize = limit
  loadCarModelList()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  currentId.value = null
  dialogTitle.value = '新增车型'
  form.name = ''
  form.brand = ''
  form.series = ''
  form.displacement = ''
  form.year = ''
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: any) => {
  isEdit.value = true
  currentId.value = row.id
  dialogTitle.value = '编辑车型'
  form.name = row.name
  form.brand = row.brand
  form.series = row.series || ''
  form.displacement = row.displacement || ''
  form.year = row.year || ''
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该车型吗？', '提示', {
      type: 'warning'
    })
    await carModelApi.deleteCarModel(row.id)
    // 删除成功（拦截器会在code不为0时抛出错误，走到这里说明成功）
    ElMessage.success('删除成功')
    loadCarModelList()
  } catch (error: any) {
    // 如果错误不是取消对话框，则显示错误信息
    if (error !== 'cancel' && error?.message !== '取消删除') {
      // 错误消息已经在拦截器中显示
      console.error('删除失败:', error)
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (isEdit.value && currentId.value) {
        await carModelApi.updateCarModel(currentId.value, { ...form })
      } else {
        await carModelApi.createCarModel({ ...form })
      }
      // 请求成功（没有抛出异常）
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      loadCarModelList()
    } catch (error) {
      console.error(isEdit.value ? '更新失败' : '创建失败', error)
      // 错误已经在拦截器中显示
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  loadCarModelList()
})
</script>

<style scoped lang="scss">
.page-container {
  padding: 20px;
}

.search-form-container {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.table-operations {
  margin-bottom: 20px;
}
</style>
