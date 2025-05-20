<template>
  <el-form
    ref="passwordFormRef"
    :model="form"
    :rules="rules"
    label-width="100px"
    @submit.prevent="onSubmit"
  >
    <el-form-item label="原密码" prop="old_password">
      <el-input
        v-model="form.old_password"
        type="password"
        placeholder="请输入原密码"
        autocomplete="current-password"
        show-password
      />
    </el-form-item>

    <el-form-item label="新密码" prop="password">
      <el-input
        v-model="form.password"
        type="password"
        placeholder="请输入新密码"
        autocomplete="new-password"
        show-password
      />
      <div class="password-strength">
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
        :type="showConfirmPassword ? 'text' : 'password'"
        placeholder="请再次输入密码"
        autocomplete="new-password"
        suffix-icon="el-icon-view"
        @click="showConfirmPassword = !showConfirmPassword"
      />
    </el-form-item>

    <el-form-item>
      <el-button
        type="primary"
        :loading="loading"
        :disabled="!canSubmit"
        @click="onSubmit"
      >
        修改密码
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { usePasswordStrength } from '@/utils/password'
import { changePassword } from '@/api/user'

const passwordFormRef = ref()

const form = reactive({
  old_password: '',
  password: '',
  confirmPassword: '',
})

const loading = ref(false)
const showConfirmPassword = ref(false)

const rules = {
  old_password: [
    { required: true, message: '请输入原密码', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 18, message: '密码长度应为6到18位', trigger: 'blur' },
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

// 密码强度逻辑
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
    form.old_password.trim() &&
    form.password.trim() &&
    form.confirmPassword.trim()
  )
})

async function onSubmit() {
  loading.value = true
  try {
    await passwordFormRef.value.validate()

    const reqData = {
      old_password: form.old_password,
      new_password: form.password,
    }

    await changePassword(reqData)

    ElMessage.success('密码修改成功')
    
  } catch (err: any) {
    ElMessage.error(err?.message || '密码修改失败，请重试')
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
