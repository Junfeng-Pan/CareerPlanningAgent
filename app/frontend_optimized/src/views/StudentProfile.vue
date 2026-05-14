<template>
  <div class="student-profile-container">
    <el-row :gutter="20">
      <!-- 左侧：基本信息和图表 -->
      <el-col :span="16">
        <!-- 技能雷达图 -->
        <el-card class="chart-card" shadow="hover" v-if="appStore.studentProfile">
          <template #header>
            <div class="card-header">
              <span><el-icon><DataAnalysis /></el-icon> 技能能力分析</span>
            </div>
          </template>

          <div ref="skillsChartRef" class="echarts-chart"></div>
        </el-card>

        <!-- 技能列表 -->
        <el-card class="skills-card" shadow="hover" v-if="appStore.studentProfile">
          <template #header>
            <div class="card-header">
              <span><el-icon><FolderOpened /></el-icon> 技能详情</span>
            </div>
          </template>

          <el-table :data="appStore.studentProfile.skills || []" style="width: 100%">
            <el-table-column type="index" width="50" />
            <el-table-column prop="name" label="技能名称" width="180" />
            <el-table-column label="技能证据">
              <template #default="{ row }">
                <el-popover placement="top" :width="300" trigger="hover">
                  <template #reference>
                    <el-tag type="info" effect="plain">
                      {{ row.evidence?.substring(0, 50) }}...
                    </el-tag>
                  </template>
                  <div style="font-size: 13px">{{ row.evidence }}</div>
                </el-popover>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：素养和潜力 -->
      <el-col :span="8">
        <!-- 职业素养 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Star /></el-icon> 职业素养</span>
            </div>
          </template>

          <div class="level-display" v-if="appStore.studentProfile?.Professionalism">
            <el-progress
              :percentage="getLevelPercentage(appStore.studentProfile.Professionalism.level)"
              :color="getLevelColor(appStore.studentProfile.Professionalism.level)"
              :format="() => appStore.studentProfile.Professionalism.level"
            />
          </div>
          <div v-else class="no-data">暂无数据</div>
        </el-card>

        <!-- 发展潜力 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><TrendCharts /></el-icon> 发展潜力</span>
            </div>
          </template>

          <div class="level-display" v-if="appStore.studentProfile?.Potential">
            <el-progress
              :percentage="getLevelPercentage(appStore.studentProfile.Potential.level)"
              :color="getLevelColor(appStore.studentProfile.Potential.level)"
              :format="() => appStore.studentProfile.Potential.level"
            />
          </div>
          <div v-else class="no-data">暂无数据</div>
        </el-card>

        <!-- 证书列表 -->
        <el-card class="info-card" shadow="hover" v-if="appStore.studentProfile?.certificates?.length">
          <template #header>
            <div class="card-header">
              <span><el-icon><Document /></el-icon> 证书列表</span>
            </div>
          </template>

          <div class="certificate-list">
            <div
              v-for="(cert, index) in appStore.studentProfile.certificates"
              :key="index"
              class="certificate-item"
            >
              <div class="cert-icon">
                <el-icon :size="24" color="#67C23A"><Award /></el-icon>
              </div>
              <div class="cert-info">
                <div class="cert-name">{{ cert.name }}</div>
                <div class="cert-evidence">{{ cert.evidence }}</div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 经历列表 -->
        <el-card class="info-card" shadow="hover" v-if="appStore.studentProfile?.Experience?.length">
          <template #header>
            <div class="card-header">
              <span><el-icon><Briefcase /></el-icon> 经历列表</span>
            </div>
          </template>

          <div class="experience-list">
            <div
              v-for="(exp, index) in appStore.studentProfile.Experience"
              :key="index"
              class="experience-item"
            >
              <div class="exp-icon">
                <el-icon :size="24" color="#409EFF"><OfficeBuilding /></el-icon>
              </div>
              <div class="exp-info">
                <div class="exp-name">{{ exp.name }}</div>
                <div class="exp-evidence">{{ exp.evidence }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 空状态 -->
    <el-empty
      v-if="!appStore.studentProfile"
      description="请先上传简历以生成学生画像"
      :image-size="200"
    >
      <el-button type="primary" @click="$router.push('/')">
        <el-icon><Upload /></el-icon>
        上传简历
      </el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { useAppStore } from '@/store/app'
import * as echarts from 'echarts'

const appStore = useAppStore()
const skillsChartRef = ref(null)
let skillsChart = null

// 初始化图表
const initSkillsChart = () => {
  if (!skillsChartRef.value || !appStore.studentProfile) return

  skillsChart = echarts.init(skillsChartRef.value)

  const skills = appStore.studentProfile.skills || []
  const maxSkills = 8

  // 准备雷达图数据
  const indicator = skills.slice(0, maxSkills).map(skill => ({
    name: skill.name,
    max: 100
  }))

  const values = skills.slice(0, maxSkills).map(() => 80) // 默认值，后续可以计算

  const option = {
    color: ['#409EFF'],
    tooltip: {},
    radar: {
      shape: 'circle',
      indicator: indicator,
      radius: '65%',
      center: ['50%', '50%'],
      axisName: {
        color: '#333',
        fontSize: 12,
        fontWeight: 'bold'
      },
      splitArea: {
        areaStyle: {
          color: ['#f8f9fa', '#e9ecef', '#dee2e6', '#ced4da']
        }
      },
      axisLine: {
        lineStyle: {
          color: '#409EFF'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#409EFF'
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '技能水平',
        areaStyle: {
          color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.1)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.5)' }
          ])
        },
        lineStyle: {
          width: 3
        },
        itemStyle: {
          color: '#409EFF',
          shadowBlur: 10,
          shadowColor: 'rgba(64, 158, 255, 0.5)'
        }
      }]
    }]
  }

  skillsChart.setOption(option)

  // 响应式调整
  window.addEventListener('resize', () => {
    skillsChart && skillsChart.resize()
  })
}

// 获取等级百分比
const getLevelPercentage = (level) => {
  const percentages = { '高': 90, '中': 60, '低': 30 }
  return percentages[level] || 50
}

// 获取等级颜色
const getLevelColor = (level) => {
  const colors = { '高': '#67C23A', '中': '#E6A23C', '低': '#F56C6C' }
  return colors[level] || '#909399'
}

// 监听数据变化
watch(() => appStore.studentProfile, () => {
  nextTick(() => {
    initSkillsChart()
  })
}, { immediate: true })

onMounted(() => {
  if (!appStore.studentProfile) {
    appStore.fetchStudentProfile()
  }
})
</script>

<style scoped lang="scss">
.student-profile-container {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.chart-card {
  margin-bottom: 20px;

  .echarts-chart {
    height: 400px;
    width: 100%;
  }
}

.skills-card {
  :deep(.el-table) {
    font-size: 13px;
  }
}

.info-card {
  margin-bottom: 20px;
}

.level-display {
  padding: 10px 0;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 20px;
}

.certificate-list, .experience-list {
  .certificate-item, .experience-item {
    display: flex;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .cert-icon, .exp-icon {
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      background: #f5f7fa;
      border-radius: 8px;
    }

    .cert-info, .exp-info {
      flex: 1;
      min-width: 0;

      .cert-name, .exp-name {
        font-weight: 600;
        color: #303133;
        margin-bottom: 4px;
      }

      .cert-evidence, .exp-evidence {
        font-size: 12px;
        color: #909399;
        line-height: 1.5;
      }
    }
  }
}
</style>
