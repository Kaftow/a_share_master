<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import {resolveIcon} from '@/utils/iconResolver'
const router = useRouter()
const route = useRoute()

const activeMenu = computed(() => route.path)

function onMenuSelect(index: string) {
  router.push(index)
}

function generateMenu(routes: readonly RouteRecordRaw[]): any[] {
  return routes
    .filter(route => route.meta?.title) 
    .map(route => {
      const menuItem: any = {
        index: route.path.startsWith('/') ? route.path : `/${route.path}`,
        title: route.meta?.title || '',
        icon: route.meta?.icon || null
      }
      if (route.children && route.children.length > 0) {
        menuItem.children = generateMenu(route.children)
      }
      return menuItem
    })
}

const menuData = computed(() => generateMenu(router.options.routes))
</script>

<template>
  <el-aside width="150px" class="sidebar">
    <el-menu
      :default-active="activeMenu"
      class="el-menu-vertical-demo"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#20a0ff"
      @select="onMenuSelect"
    >
      <template v-for="item in menuData" :key="item.index">
        <el-sub-menu v-if="item.children" :index="item.index">
          <template #title>
            <div class="menu-title">
              <span>{{ item.title }}</span>
              <el-icon v-if="item.icon"><component :is="resolveIcon(item.icon)" /></el-icon>
            </div>
          </template>
          <el-menu-item
            v-for="child in item.children"
            :key="child.index"
            :index="child.index"
          >
            {{ child.title }}
          </el-menu-item>
        </el-sub-menu>
        <el-menu-item v-else :index="item.index">
          <template #title>
            <div class="menu-title">
              <span>{{ item.title }}</span>
              <el-icon v-if="item.icon"><component :is="resolveIcon(item.icon)" /></el-icon>
            </div>
          </template>
        </el-menu-item>
      </template>
    </el-menu>
  </el-aside>
</template>

<style scoped>
.sidebar {
  background-color: #304156;
  color: #fff;
  height: 100vh; /* 侧边栏撑满全高 */
  border-right: none;
}

.el-menu-item__content, 
.el-sub-menu__title {
  display: flex;
  align-items: center;
  gap: 8px; /* 图标和文字间距 */
}

.el-menu-item > .el-tooltip {
  display: flex !important;
  align-items: center;
}

.el-menu-item > span {
  line-height: 15px;
  vertical-align: middle;
}

.menu-title {
  display: flex;
  justify-content: space-between; /* 左右分散 */
  align-items: center;            /* 垂直居中 */
  width: 100%;
  padding-right: 12px;            /* 右侧留点空间给图标 */
}

</style>
