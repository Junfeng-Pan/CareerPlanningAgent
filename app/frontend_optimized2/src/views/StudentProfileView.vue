<template>
  <div class="student-profile-view">
    <div class="page-header">
      <h2>学生能力画像</h2>
      <el-button type="primary" @click="loadProfile" :loading="loading">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="error" class="error-container">
      <el-result icon="error" title="加载失败" :sub-title="error">
        <template #extra>
          <el-button type="primary" @click="loadProfile">重新加载</el-button>
        </template>
      </el-result>
    </div>

    <div v-else-if="!profile" class="empty-container">
      <el-result icon="info" title="暂无数据" sub-title="请先上传简历以生成学生画像">
        <template #extra>
          <el-button type="primary" @click="$router.push('/')">去上传简历</el-button>
        </template>
      </el-result>
    </div>

    <div v-else class="profile-content">
      <!-- 基本信息 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <el-icon><User /></el-icon>
            <span>基本信息</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ profile.name || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="学历">
            {{ profile.education?.degree || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="毕业院校">
            {{ profile.education?.university || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="专业">
            {{ profile.education?.major || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="毕业年份">
            {{ profile.education?.graduation_year || '未填写' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 能力维度雷达图 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <el-icon><DataAnalysis /></el-icon>
            <span>能力维度分析</span>
          </div>
        </template>
        <div ref="radarChart" class="echart"></div>
      </el-card>

      <!-- 专业技能 -->
      <el-card class="skills-card">
        <template #header>
          <div class="card-header">
            <el-icon><Setting /></el-icon>
            <span>专业技能</span>
          </div>
        </template>
        <el-empty v-if="!profile.skills?.length" description="暂无技能信息" />
        <div v-else class="skills-list">
          <el-tag
            v-for="(skill, index) in profile.skills"
            :key="index"
            class="skill-tag"
            :type="getSkillType(index)"
            size="large"
            effect="plain"
          >
            {{ skill.name }}
          </el-tag>
        </div>
        <el-collapse v-if="profile.skills?.length" class="skill-details">
          <el-collapse-item
            v-for="(skill, index) in profile.skills"
            :key="index"
            :title="skill.name"
            :name="index"
          >
            <div class="skill-evidence">
              <el-text type="info">证据：</el-text>
              <p>{{ skill.evidence || '无详细信息' }}</p>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-card>

      <!-- 证书列表 -->
      <el-card class="certificates-card">
        <template #header>
          <div class="card-header">
            <el-icon><Award /></el-icon>
            <span>证书资质</span>
          </div>
        </template>
        <el-empty v-if="!profile.certificates?.length" description="暂无证书信息" />
        <el-timeline v-else>
          <el-timeline-item
            v-for="(cert, index) in profile.certificates"
            :key="index"
            :icon="Award"
            size="large"
          >
            <el-card>
              <h4>{{ cert.name }}</h4>
              <p class="evidence">{{ cert.evidence }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>

      <!-- 项目与实习经历 -->
      <el-card class="experience-card">
        <template #header>
          <div class="card-header">
            <el-icon><Briefcase /></el-icon>
            <span>项目与实习经历</span>
          </div>
        </template>
        <el-empty v-if="!profile.Experience?.length" description="暂无经历信息" />
        <el-timeline v-else>
          <el-timeline-item
            v-for="(exp, index) in profile.Experience"
            :key="index"
            :icon="Briefcase"
            size="large"
          >
            <el-card>
              <h4>{{ exp.name }}</h4>
              <p class="evidence">{{ exp.evidence }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>

      <!-- 职业素养与发展潜力 -->
      <el-row :gutter="16">
        <el-col :span="12">
          <el-card class="level-card">
            <template #header>
              <div class="card-header">
                <el-icon><Star /></el-icon>
                <span>职业素养</span>
              </div>
            </template>
            <div class="level-display" :class="getLevelClass(profile.Professionalism?.level)">
              {{ profile.Professionalism?.level || '未评估' }}
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="level-card">
            <template #header>
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>发展潜力</span>
              </div>
            </template>
            <div class="level-display" :class="getLevelClass(profile.Potential?.level)">
              {{ profile.Potential?.level || '未评估' }}
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { getStudentProfile } from '@/api/services'
import * as echarts from 'echarts'

const loading = ref(false)
const error = ref('')
const profile = ref(null)
const radarChart = ref(null)

const getSessionId = () => window.getSessionId?.() || ''

// 加载学生画像
const loadProfile = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await getStudentProfile(getSessionId())
    profile.value = response.student_profile

    if (profile.value) {
      await nextTick()
      initRadarChart()
    }
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

// 获取技能标签类型
const getSkillType = (index) => {
  const types = ['primary', 'success', 'warning', 'info', 'danger']
  return types[index % types.length]
}

// 获取等级样式
const getLevelClass = (level) => {
  const map = {
    '高': 'level-high',
    '中': 'level-medium',
    '低': 'level-low'
  }
  return map[level] || ''
}

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChart.value) return

  const isDark = document.documentElement.getAttribute('data-theme') !== 'light'
  const chart = echarts.init(radarChart.value, isDark ? 'dark' : null, {
    renderer: 'canvas',
    devicePixelRatio: window.devicePixelRatio
  })

  // 构建雷达图数据
  const indicators = []
  const values = []

  // 技能数量
  const skillCount = profile.value.skills?.length || 0
  if (skillCount > 0) {
    indicators.push({ name: '专业技能', max: 100 })
    values.push(Math.min(skillCount * 15, 100))
  }

  // 证书数量
  const certCount = profile.value.certificates?.length || 0
  if (certCount > 0) {
    indicators.push({ name: '证书资质', max: 100 })
    values.push(Math.min(certCount * 25, 100))
  }

  // 经历数量
  const expCount = profile.value.Experience?.length || 0
  if (expCount > 0) {
    indicators.push({ name: '实践经历', max: 100 })
    values.push(Math.min(expCount * 20, 100))
  }

  // 职业素养
  const profLevel = profile.value.Professionalism?.level
  if (profLevel) {
    indicators.push({ name: '职业素养', max: 100 })
    const profMap = { '高': 90, '中': 60, '低': 30 }
    values.push(profMap[profLevel] || 50)
  }

  // 发展潜力
  const potentialLevel = profile.value.Potential?.level
  if (potentialLevel) {
    indicators.push({ name: '发展潜力', max: 100 })
    const potentialMap = { '高': 90, '中': 60, '低': 30 }
    values.push(potentialMap[potentialLevel] || 50)
  }

  // 如果没有数据，添加默认
  if (indicators.length === 0) {
    indicators.push(
      { name: '专业技能', max: 100 },
      { name: '证书资质', max: 100 },
      { name: '实践经历', max: 100 },
      { name: '职业素养', max: 100 },
      { name: '发展潜力', max: 100 }
    )
    values.push(0, 0, 0, 0, 0)
  }

  const option = {
    color: ['var(--primary-color)'],
    tooltip: {},
    radar: {
      indicator: indicators,
      shape: 'circle',
      splitNumber: 5,
      axisName: {
        color: 'var(--text-primary)',
        fontSize: 14
      },
      splitLine: {
        lineStyle: {
          color: 'var(--border-color)'
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(137, 180, 250, 0.1)', 'rgba(137, 180, 250, 0.05)']
        }
      },
      axisLine: {
        lineStyle: {
          color: 'var(--text-tertiary)'
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '能力评估',
        areaStyle: {
          color: 'rgba(137, 180, 250, 0.3)'
        },
        lineStyle: {
          width: 2
        },
        itemStyle: {
          color: 'var(--primary-color)'
        }
      }]
    }]
  }

  chart.setOption(option)

  // 响应式
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.student-profile-view {
  padding: 24px;
  height: 100%;
  overflow-y: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  color: var(--text-primary);
  margin: 0;
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
  font-weight: 500;
}

.echart {
  height: 350px;
  width: 100%;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.skill-tag {
  font-size: 14px;
  padding: 6px 16px;
}

.skill-details {
  background-color: var(--bg-tertiary);
  border-radius: 8px;
}

.skill-evidence {
  padding: 8px 0;
}

.skill-evidence p {
  margin: 8px 0 0 0;
  line-height: 1.6;
  color: var(--text-secondary);
}

.evidence {
  margin-top: 8px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.level-card :deep(.el-card__body) {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.level-display {
  font-size: 36px;
  font-weight: bold;
  padding: 16px 48px;
  border-radius: 12px;
}

.level-high {
  background-color: rgba(166, 227, 161, 0.2);
  color: var(--success-color);
}

.level-medium {
  background-color: rgba(250, 227, 133, 0.2);
  color: var(--warning-color);
}

.level-low {
  background-color: rgba(243, 139, 168, 0.2);
  color: var(--danger-color);
}
</style>
