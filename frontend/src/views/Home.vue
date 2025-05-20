<template>
  <div class="home">
    <el-card class="welcome-card">
      <h2>欢迎使用 A股大王 🏆</h2>
      <p>这是一个面向 A 股投资者的数据服务平台。</p>
      <el-divider />
      <p>
        你可以在左侧导航栏中访问用户中心、注册登录、修改密码等功能，
        也可以在此平台获取股票数据、交易日历等信息。
      </p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.home {
  display: flex;
  justify-content: center;
  padding-top: 100px;
}

.welcome-card {
  width: 600px;
  text-align: center;
  background: #ffffff;
}
</style>
