<template>
  <div class="app-container" :data-theme="currentTheme">
    <el-container>
      <!-- 侧边导航栏 -->
      <el-aside width="220px">
        <div class="logo">
          <el-icon :size="28"><Reading /></el-icon>
          <span>职业规划智能体</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          router
          :background-color="themeColors.sidebarBg"
          :text-color="themeColors.sidebarText"
          :active-text-color="themeColors.activeText"
        >
          <el-menu-item index="/">
            <el-icon><ChatDotRound /></el-icon>
            <span>智能对话</span>
          </el-menu-item>
          <el-menu-item index="/student-profile">
            <el-icon><User /></el-icon>
            <span>学生画像</span>
          </el-menu-item>
          <el-menu-item index="/job-profile">
            <el-icon><Briefcase /></el-icon>
            <span>岗位画像</span>
          </el-menu-item>
          <el-menu-item index="/match-result">
            <el-icon><DataAnalysis /></el-icon>
            <span>人岗匹配</span>
          </el-menu-item>
        </el-menu>
        <div class="session-info" v-if="sessionId">
          <el-text size="small" type="info">会话 ID:</el-text>
          <el-text size="small" class="session-id">{{ sessionIdDisplay }}</el-text>
          <el-button size="small" type="danger" link @click="clearSession">
            清除会话
          </el-button>
        </div>
        <!-- 主题切换按钮 -->
        <div class="theme-switcher">
          <el-button
            class="theme-toggle-btn"
            @click="toggleTheme"
            :title="currentTheme === 'dark' ? '切换到浅色模式' : '切换到深色模式'"
          >
            <el-icon v-if="currentTheme === 'dark'"><Light /></el-icon>
            <el-icon v-else><Odometer /></el-icon>
            <span class="theme-text">{{ currentTheme === 'dark' ? '浅色' : '深色' }}</span>
          </el-button>
        </div>
      </el-aside>

      <!-- 主内容区 -->
      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { deleteSession } from '@/api/services'

const route = useRoute()

// 主题管理
const currentTheme = ref(localStorage.getItem('theme') || 'dark')

// 应用主题
const applyTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
}

// 初始化主题
onMounted(() => {
  applyTheme(currentTheme.value)
})

// 切换主题
const toggleTheme = () => {
  currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
  applyTheme(currentTheme.value)
  ElMessage.success(`已切换到${currentTheme.value === 'dark' ? '深色' : '浅色'}模式`)
}

// 主题颜色配置
const themeColors = {
  sidebarBg: 'var(--sidebar-bg)',
  sidebarText: 'var(--sidebar-text)',
  activeText: 'var(--primary-color)'
}

// 会话 ID 管理
const sessionId = ref(localStorage.getItem('session_id') || '')

// 监听会话 ID 变化
watch(sessionId, (newId) => {
  if (newId) {
    localStorage.setItem('session_id', newId)
  } else {
    localStorage.removeItem('session_id')
  }
})

// 暴露 sessionId 给子组件
provideSessionId(sessionId)

const activeMenu = computed(() => route.path)

const sessionIdDisplay = computed(() => {
  if (!sessionId.value) return ''
  const id = sessionId.value
  return id.length > 12 ? `${id.slice(0, 8)}...${id.slice(-4)}` : id
})

// 清除会话
const clearSession = async () => {
  try {
    if (sessionId.value) {
      await deleteSession(sessionId.value)
    }
    sessionId.value = ''
    ElMessage.success('会话已清除')
  } catch (e) {
    sessionId.value = ''
    ElMessage.warning('会话已清除（服务器无此会话）')
  }
}

// 提供 sessionId 给子组件
function provideSessionId(sessionIdRef) {
  // 通过 custom event 或 provide/inject 共享
}

// 暴露 sessionId 更新方法
window.updateSessionId = (id) => {
  sessionId.value = id
}

window.getSessionId = () => sessionId.value
</script>

<style scoped>
.app-container {
  height: 100vh;
  overflow: hidden;
}

.el-container {
  height: 100%;
}

.el-aside {
  background-color: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color);
  transition: background-color 0.2s ease;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 20px;
  color: var(--sidebar-text);
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid var(--border-color);
}

.el-menu {
  flex: 1;
  border-right: none;
  padding-top: 10px;
}

.el-menu-item {
  margin: 4px 8px;
  border-radius: 8px;
}

.el-menu-item:hover {
  background-color: var(--hover-color) !important;
}

.el-menu-item.is-active {
  background-color: var(--hover-color) !important;
}

.session-info {
  padding: 15px;
  border-top: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.session-id {
  font-family: monospace;
  color: var(--primary-color);
}

.el-main {
  background-color: var(--bg-primary);
  padding: 0;
  overflow-y: auto;
  transition: background-color 0.2s ease;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 主题切换按钮 */
.theme-switcher {
  padding: 15px;
  border-top: 1px solid var(--border-color);
}

.theme-toggle-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: var(--hover-color);
  border: none;
  color: var(--sidebar-text);
}

.theme-toggle-btn:hover {
  background-color: var(--border-color);
}

.theme-text {
  font-size: 13px;
}
</style>
