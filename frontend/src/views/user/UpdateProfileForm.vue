<template>
  <el-form
    ref="updateProfileFormRef"
    :model="form"
    :rules="rules"
    label-width="100px"
    @submit.prevent="onSubmit"
  >
    <el-form-item label="昵称" prop="nickname">
      <el-input v-model="form.nickname" placeholder="请输入昵称" />
    </el-form-item>

    <el-form-item label="邮箱" prop="email">
      <el-input v-model="form.email" placeholder="请输入邮箱" autocomplete="email" />
    </el-form-item>

    <el-form-item label="性别" prop="gender">
      <el-radio-group v-model="genderOption" @change="onGenderChange">
        <el-radio label="male">男</el-radio>
        <el-radio label="female">女</el-radio>
        <el-radio label="custom">自定义</el-radio>
      </el-radio-group>
      <el-input
        v-if="genderOption === 'custom'"
        v-model="form.gender"
        placeholder="请输入自定义性别"
        :maxlength="10"
        show-word-limit
        class="mt-2"
      />
    </el-form-item>

    <el-form-item label="生日" prop="birth_date">
      <el-date-picker
        v-model="form.birth_date"
        type="date"
        placeholder="选择生日"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        clearable
      />
    </el-form-item>

    <el-form-item label="国家" prop="country">
      <el-input v-model="form.country" placeholder="请输入国家" />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" :loading="loading" :disabled="!canSubmit" @click="onSubmit">
        保存资料
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { UserUpdateRequest } from '@/types/user'
import { updateUserProfile, getUserProfile } from '@/api/user'

const updateProfileFormRef = ref()
const form = reactive<UserUpdateRequest>({
  nickname: '',
  email: '',
  gender: 'male',
  birth_date: '',
  country: '',
})

// 初始化匹配值
const genderOption = ref<'male' | 'female' | 'custom'>('male')
// 保存自定义性别值
const customGenderValue = ref('')

const onGenderChange = (val: string) => {
  if (val === 'custom') {
    form.gender = customGenderValue.value || '' 
  } else {
    if (genderOption.value === 'custom' && form.gender?.trim()) {
      customGenderValue.value = form.gender
    }
    form.gender = val // 设置为选择的预设值
  }
}

onMounted(async () => {
  try {
    const userData = await getUserProfile()
    
    if (!userData) return
    
    // 更新表单数据
    Object.assign(form, userData)
    
    // 根据已有性别值设置正确的UI状态
    if (form.gender) {
      if (['male', 'female'].includes(form.gender)) {
        genderOption.value = form.gender as 'male' | 'female'
      } else {
        genderOption.value = 'custom'
        customGenderValue.value = form.gender
      }
    }
  } catch (error) {
    console.error('Failed to load user profile:', error)
    ElMessage.error('获取用户信息失败，请稍后再试')
  }
})

const loading = ref(false)

const rules = {
  nickname: [
    { required: false, message: '请输入昵称', trigger: ['blur', 'change'] },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: ['blur', 'change'] },
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] },
  ],
  gender: [
    {
      validator: (_: any, value: string, callback: any) => {
        if (genderOption.value === 'custom') {
          if (!value || value.trim() === '') {
            callback(new Error('请输入自定义性别'))
          } else if (value.length > 10) {
            callback(new Error('自定义性别最多10个字符'))
          } else {
            callback()
          }
        } else {
          callback()
        }
      },
      trigger: ['blur', 'change'],
    },
  ],
}

const canSubmit = computed(() => {
  return (form.email?.trim() || '') !== '' && 
         (genderOption.value !== 'custom' || (form.gender && form.gender.trim() !== ''))
})

async function onSubmit() {
  loading.value = true
  try {
    await updateProfileFormRef.value.validate()
    await updateUserProfile(form)
    ElMessage.success('资料更新成功')
  } catch (err: any) {
    ElMessage.error(err?.message || '资料更新失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.mt-2 {
  margin-top: 8px;
}
</style>