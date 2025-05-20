<template>
  <el-form
    ref="registerFormRef"
    :model="form"
    :rules="rules"
    label-width="100px"
    @submit.prevent="onSubmit"
  >
    <el-form-item label="用户名" prop="username">
      <el-input
        v-model="form.username"
        placeholder="请输入用户名"
        autocomplete="username"
        autofocus
      />
    </el-form-item>

    <el-form-item label="邮箱" prop="email">
      <el-input
        v-model="form.email"
        placeholder="请输入邮箱"
        autocomplete="email"
      />
    </el-form-item>

    <el-form-item label="昵称（可选）" prop="nickname">
      <el-input
        v-model="form.nickname"
        placeholder="请输入昵称"
        autocomplete="nickname"
      />
    </el-form-item>

    <el-form-item label="密码" prop="password">
  <el-input
    v-model="form.password"
    placeholder="请输入密码"
    autocomplete="new-password"
    show-password
  />
  <div class="password-strength" v-if="form.password.trim() !== ''">
    <el-progress
      :percentage="passwordStrengthPercent"
      :status="passwordStrengthStatus"
      :stroke-width="6"
      show-text="false"
    />
    <span class="strength-text">{{ passwordStrengthText }}</span>
  </div>
</el-form-item>

<el-form-item label="确认密码" prop="confirmPassword">
  <el-input
    v-model="form.confirmPassword"
    placeholder="请再次输入密码"
    autocomplete="new-password"
    show-password
  />
</el-form-item>


    <el-form-item>
      <el-button
        type="primary"
        :loading="loading"
        :disabled="!canSubmit"
        @click="onSubmit"
      >
        注册
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { usePasswordStrength } from '@/utils/password'
import { registerUser } from '@/api/user'

const registerFormRef = ref()

const form = reactive({
  username: '',
  email: '',
  nickname: '',
  password: '',
  confirmPassword: '',
})

const loading = ref(false)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 15, message: '长度在3到15个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] },
  ],
  nickname: [
    { max: 20, message: '昵称最多20个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 18, message: '密码长度应为8到18位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string) => {
        return new Promise<void>((resolve, reject) => {
          if (value !== form.password) {
            reject(new Error('两次输入密码不一致'))
          } else {
            resolve()
          }
        })
      },
      trigger: 'blur',
    },
  ],
}

const passwordRef = ref(form.password)
watch(() => form.password, (val) => {
  passwordRef.value = val
})

const { score, feedback } = usePasswordStrength(passwordRef)

const passwordStrengthPercent = computed(() => (score.value + 1) * 20)
const passwordStrengthText = computed(() => feedback.value.level)
const passwordStrengthStatus = computed(() => {
  switch (score.value) {
    case 0:
    case 1:
      return 'exception'
    case 2:
      return 'warning'
    case 3:
    case 4:
      return 'success'
    default:
      return 'exception'
  }
})

const canSubmit = computed(() => {
  return (
    form.username.trim() !== '' &&
    form.email.trim() !== '' &&
    form.password.trim() !== '' &&
    form.confirmPassword.trim() !== ''
  )
})

async function onSubmit() {
  loading.value = true
  try {
    await registerFormRef.value.validate()

    const reqData: any = {
      username: form.username,
      email: form.email,
      password: form.password,
    }
    if (form.nickname.trim()) {
      reqData.nickname = form.nickname.trim()
    }

    await registerUser(reqData)

    ElMessage.success('注册成功！请登录。')
    // 这里可以跳转登录页或者清空表单
  } catch (err: any) {
    if (err?.message) {
      ElMessage.error(err.message)
    } else {
      ElMessage.error('注册失败，请重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.password-strength {
  display: flex;
  align-items: center;
  margin-top: 6px;
}
.strength-text {
  margin-left: 10px;
  font-weight: 600;
  color: #666;
}
</style>

