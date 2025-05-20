<template>
  <el-form
    ref="loginFormRef"
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

    <el-form-item label="密码" prop="password">
      <el-input
        v-model="form.password"
        type="password"
        placeholder="请输入密码"
        autocomplete="current-password"
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
        登录
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { loginUser } from '@/api/user'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const loginFormRef = ref()
const form = reactive({
  username: '',
  password: '',
})

const loading = ref(false)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
  ],
}

const canSubmit = computed(() => form.username.trim() !== '' && form.password.trim() !== '')

async function onSubmit() {
  loading.value = true
  try {
    await loginFormRef.value.validate()
    const res = await loginUser({
      username: form.username,
      password: form.password,
    })
    const token = res.access_token
    const expiresIn = res.expires_in
    userStore.setToken(token, expiresIn)
    ElMessage.success('登录成功！')
    // 登录成功后跳转或其他操作
  } catch (err: any) {
    ElMessage.error(err?.message || '登录失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>
