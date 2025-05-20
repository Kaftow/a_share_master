<template>
  <el-button type="danger" :loading="loading" @click="confirmDelete">
    注销账户
  </el-button>

  <el-dialog
    title="确认注销账户"
    :visible.sync="dialogVisible"
    width="400px"
    :before-close="handleClose"
  >
    <span>注销账户操作不可逆，确定要删除账户吗？</span>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="danger" :loading="loading" @click="onDelete">确定注销</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { deleteAccount } from '@/api/user'

const loading = ref(false)
const dialogVisible = ref(false)

function confirmDelete() {
  dialogVisible.value = true
}

function handleClose(done: () => void) {
  if (!loading.value) {
    done()
  }
}

async function onDelete() {
  loading.value = true
  try {
    await deleteAccount()
    ElMessage.success('账户已成功注销，正在跳转登录页...')
    dialogVisible.value = false
    // 跳转登录页
    // router.push('/login')
  } catch (err: any) {
    ElMessage.error(err?.message || '注销失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>
