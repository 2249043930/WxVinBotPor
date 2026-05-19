<template>
  <div class="login-page">
    <div class="login-left">
      <div class="login-brand">WxVinBot Por</div>
      <div class="login-desc">
        汽车配件询价管理系统<br>
        智能化车架号识别，高效管理汽配业务
      </div>
    </div>
    <div class="login-right">
      <div class="login-box">
        <h2 class="login-title">欢迎登录</h2>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入登录账号"
              size="large"
              :prefix-icon="User"
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="captcha">
            <div class="captcha-input">
              <el-input
                v-model="form.captcha"
                placeholder="请输入验证码"
                size="large"
                :prefix-icon="Key"
                clearable
              />
              <div class="captcha-img" @click="refreshCaptcha">
                {{ captchaCode }}
              </div>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="form.remember">记住密码</el-checkbox>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Key } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const captchaCode = ref('')

const form = reactive({
  username: '',
  password: '',
  captcha: '',
  remember: false
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入登录账号', trigger: 'blur' },
    { min: 4, max: 20, message: '账号长度4-20位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度6-20位', trigger: 'blur' }
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 4, message: '验证码为4位', trigger: 'blur' }
  ]
}

const generateCaptcha = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  let code = ''
  for (let i = 0; i < 4; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  captchaCode.value = code
}

const refreshCaptcha = () => {
  generateCaptcha()
  form.captcha = ''
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    if (form.captcha.toUpperCase() !== captchaCode.value) {
      ElMessage.error('验证码错误')
      refreshCaptcha()
      return
    }
    
    loading.value = true
    try {
      const success = await userStore.login({
        username: form.username,
        password: form.password,
        captcha: form.captcha,
        remember: form.remember
      })
      
      if (success) {
        ElMessage.success('登录成功')
        router.push('/dashboard')
      }
    } finally {
      loading.value = false
    }
  })
}

onMounted(() => {
  generateCaptcha()
})
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #fff;
  padding: var(--spacing-xl);
}

.login-brand {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: var(--spacing-md);
}

.login-desc {
  font-size: 18px;
  opacity: 0.9;
  text-align: center;
  max-width: 400px;
  line-height: 1.6;
}

.login-right {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--bg-base);
}

.login-box {
  width: 400px;
  background: var(--bg-white);
  border-radius: var(--border-radius-large);
  box-shadow: var(--shadow-light);
  padding: var(--spacing-xl);
}

.login-title {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  margin-bottom: var(--spacing-xl);
  color: var(--text-primary);
}

.login-form :deep(.el-input__wrapper) {
  padding: 4px 11px;
}

.login-form :deep(.el-input__inner) {
  height: 40px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  background: linear-gradient(135deg, #409EFF 0%, #337ECC 100%);
  border: none;
}

.login-btn:hover {
  background: linear-gradient(135deg, #66b1ff 0%, #409EFF 100%);
}

.captcha-input {
  display: flex;
  gap: var(--spacing-md);
  width: 100%;
}

.captcha-input .el-input {
  flex: 1;
}

.captcha-img {
  width: 120px;
  height: 40px;
  border-radius: var(--border-radius-base);
  cursor: pointer;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  color: var(--text-primary);
  letter-spacing: 4px;
  user-select: none;
}

.captcha-img:hover {
  background: linear-gradient(135deg, #e4e7ed 0%, #d3d6dd 100%);
}
</style>
