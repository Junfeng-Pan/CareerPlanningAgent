<template>
  <div class="match-result-view">
    <div class="page-header">
      <h2>人岗匹配结果</h2>
      <el-button type="primary" @click="loadResult" :loading="loading">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="error" class="error-container">
      <el-result icon="error" title="加载失败" :sub-title="error">
        <template #extra>
          <el-button type="primary" @click="loadResult">重新加载</el-button>
        </template>
      </el-result>
    </div>

    <div v-else-if="!result" class="empty-container">
      <el-result icon="info" title="暂无数据" sub-title="请先上传简历并分析岗位以生成匹配结果">
        <template #extra>
          <el-button type="primary" @click="$router.push('/')">去上传简历</el-button>
          <el-button type="success" @click="$router.push('/job-profile')">分析岗位</el-button>
        </template>
      </el-result>
    </div>

    <div v-else class="result-content">
      <!-- 匹配置信度概览 -->
      <el-row :gutter="16" class="overview-row">
        <el-col :span="8">
          <el-card class="degree-card">
            <div class="degree-title">匹配度</div>
            <div class="degree-display" :class="getDegreeClass(result.summary?.matching_degree)">
              {{ result.summary?.matching_degree || '未知' }}
            </div>
          </el-card>
        </el-col>
        <el-col :span="16">
          <el-card class="summary-card">
            <div class="summary-title">匹配总结</div>
            <div class="summary-text">{{ result.summary?.summary || '暂无总结' }}</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 雷达图对比 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <el-icon><DataAnalysis /></el-icon>
            <span>能力匹配雷达图</span>
          </div>
        </template>
        <div ref="radarChart" class="echart"></div>
      </el-card>

      <!-- 优势与差距 -->
      <el-row :gutter="16">
        <el-col :span="12">
          <el-card class="advantages-card">
            <template #header>
              <div class="card-header">
                <el-icon><CircleCheck /></el-icon>
                <span>优势</span>
              </div>
            </template>
            <el-empty v-if="!result.summary?.advantages?.length" description="暂无优势项" />
            <ul v-else class="list-container">
              <li v-for="(item, index) in result.summary.advantages" :key="index">
                <el-icon :size="18" color="#a6e3a1"><CircleCheckFilled /></el-icon>
                <span>{{ item }}</span>
              </li>
            </ul>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="gaps-card">
            <template #header>
              <div class="card-header">
                <el-icon><CircleClose /></el-icon>
                <span>差距</span>
              </div>
            </template>
            <el-empty v-if="!result.summary?.gaps?.length" description="暂无差距项" />
            <ul v-else class="list-container">
              <li v-for="(item, index) in result.summary.gaps" :key="index">
                <el-icon :size="18" color="#f38ba8"><CircleCloseFilled /></el-icon>
                <span>{{ item }}</span>
              </li>
            </ul>
          </el-card>
        </el-col>
      </el-row>

      <!-- 技能匹配详情 -->
      <el-card class="skills-card">
        <template #header>
          <div class="card-header">
            <el-icon><Setting /></el-icon>
            <span>技能匹配详情</span>
          </div>
        </template>
        <el-empty v-if="!result.skills?.length" description="暂无技能数据" />
        <div v-else class="skills-table">
          <el-table :data="result.skills" stripe :header-cell-style="{ background: '#181825', color: '#cdd6f4' }">
            <el-table-column prop="name" label="技能名称" min-width="180" />
            <el-table-column label="要求" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="row.required ? 'primary' : 'info'" size="small">
                  {{ row.required ? '必需' : '加分' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="匹配状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ row.status || '未知' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="student_evidence" label="学生证据" min-width="200">
              <template #default="{ row }">
                <el-text v-if="row.student_evidence" type="info" size="small">
                  {{ row.student_evidence }}
                </el-text>
                <el-text v-else type="info" size="small">无相关证据</el-text>
              </template>
            </el-table-column>
            <el-table-column prop="gap_analysis" label="差距分析" min-width="200">
              <template #default="{ row }">
                <el-text v-if="row.gap_analysis" type="warning" size="small">
                  {{ row.gap_analysis }}
                </el-text>
                <el-text v-else type="success" size="small">符合要求</el-text>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>

      <!-- 岗位要求对比 -->
      <el-row :gutter="16">
        <el-col :span="12">
          <el-card class="thresholds-card">
            <template #header>
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <span>基础门槛对比</span>
              </div>
            </template>
            <el-empty v-if="!result.thresholds?.length" description="暂无门槛数据" />
            <div v-else class="compare-list">
              <div v-for="(item, index) in result.thresholds" :key="index" class="compare-item">
                <div class="compare-name">{{ item.name }}</div>
                <div class="compare-evidence">{{ item.evidence }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="professionalism-card">
            <template #header>
              <div class="card-header">
                <el-icon><Star /></el-icon>
                <span>职业素养对比</span>
              </div>
            </template>
            <el-empty v-if="!result.professionalism?.length" description="暂无素养数据" />
            <div v-else class="compare-list">
              <div v-for="(item, index) in result.professionalism" :key="index" class="compare-item">
                <div class="compare-name">{{ item.name }}</div>
                <div class="compare-evidence">{{ item.evidence }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 推荐建议 -->
      <el-card class="recommendations-card">
        <template #header>
          <div class="card-header">
            <el-icon><Lightbulb /></el-icon>
            <span>推荐建议</span>
          </div>
        </template>
        <el-empty v-if="!result.recommendations?.length" description="暂无推荐建议" />
        <div v-else class="recommendations-list">
          <div v-for="(item, index) in result.recommendations" :key="index" class="recommendation-item">
            <el-icon :size="20" color="#f9e2af"><Lightbulb /></el-icon>
            <span>{{ item }}</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMatchResult } from '@/api/services'
import * as echarts from 'echarts'

const loading = ref(false)
const error = ref('')
const result = ref(null)
const radarChart = ref(null)
let chartInstance = null

const getSessionId = () => window.getSessionId?.() || ''

// 加载匹配结果
const loadResult = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await getMatchResult(getSessionId())
    result.value = response.match_result

    if (result.value) {
      await nextTick()
      // 等待卡片渲染完成
      setTimeout(() => {
        initRadarChart()
      }, 100)
    }
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

// 获取匹配度样式
const getDegreeClass = (degree) => {
  const map = {
    '高': 'degree-high',
    '中': 'degree-medium',
    '低': 'degree-low'
  }
  return map[degree] || ''
}

// 获取状态类型
const getStatusType = (status) => {
  const map = {
    '具备': 'success',
    '部分具备': 'warning',
    '缺失': 'danger',
    '未知': 'info'
  }
  return map[status] || 'info'
}

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChart.value) {
    console.error('雷达图容器不存在')
    return
  }

  // 销毁旧图表
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 根据当前主题初始化
  const isDark = document.documentElement.getAttribute('data-theme') !== 'light'
  chartInstance = echarts.init(radarChart.value, isDark ? 'dark' : null, {
    renderer: 'canvas',
    devicePixelRatio: window.devicePixelRatio
  })

  // 构建雷达图数据 - 学生 vs 岗位
  const skills = result.value.skills || []

  // 提取技能名称作为维度
  const indicators = skills.map(s => ({
    name: s.name.length > 8 ? s.name.slice(0, 8) + '...' : s.name,
    max: 100
  }))

  // 学生分数
  const studentValues = skills.map(s => {
    if (s.status === '具备') return 90
    if (s.status === '部分具备') return 60
    if (s.status === '缺失') return 20
    return 50
  })

  // 岗位要求分数（都是 100，因为是标准要求）
  const jobValues = skills.map(() => 100)

  // 如果没有数据，使用默认
  if (indicators.length === 0) {
    for (let i = 0; i < 5; i++) {
      indicators.push({ name: `维度${i + 1}`, max: 100 })
      studentValues.push(0)
      jobValues.push(100)
    }
  }

  const option = {
    color: ['var(--success-color)', 'var(--danger-color)'],
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.seriesIndex === 0) {
          return `${params.name}: ${params.value} 分`
        }
        return `岗位要求：${params.value} 分`
      }
    },
    legend: {
      data: ['学生能力', '岗位要求'],
      textStyle: {
        color: 'var(--text-primary)'
      },
      bottom: 10
    },
    radar: {
      indicator: indicators,
      shape: 'circle',
      splitNumber: 5,
      axisName: {
        color: 'var(--text-primary)',
        fontSize: 12
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
      data: [
        {
          value: studentValues,
          name: '学生能力',
          areaStyle: {
            color: 'rgba(166, 227, 161, 0.3)'
          },
          lineStyle: {
            width: 2
          },
          itemStyle: {
            color: 'var(--success-color)'
          }
        },
        {
          value: jobValues,
          name: '岗位要求',
          areaStyle: {
            color: 'rgba(243, 139, 168, 0.2)'
          },
          lineStyle: {
            width: 2,
            type: 'dashed'
          },
          itemStyle: {
            color: 'var(--danger-color)'
          }
        }
      ]
    }]
  }

  chartInstance.setOption(option)

  // 响应式调整
  const handleResize = () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  }
  window.addEventListener('resize', handleResize)

  // 保存清理函数
  chartInstance.cleanupResize = () => {
    window.removeEventListener('resize', handleResize)
  }
}

// 组件卸载时清理
onUnmounted(() => {
  if (chartInstance) {
    if (chartInstance.cleanupResize) {
      chartInstance.cleanupResize()
    }
    chartInstance.dispose()
    chartInstance = null
  }
})

onMounted(() => {
  loadResult()
})
</script>

<style scoped>
.match-result-view {
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

.result-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.overview-row {
  margin-bottom: 8px;
}

.degree-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.degree-title {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.degree-display {
  font-size: 48px;
  font-weight: bold;
  padding: 16px 32px;
  border-radius: 16px;
}

.degree-high {
  background: linear-gradient(135deg, rgba(166, 227, 161, 0.2), rgba(166, 227, 161, 0.1));
  color: var(--success-color);
}

.degree-medium {
  background: linear-gradient(135deg, rgba(250, 227, 133, 0.2), rgba(250, 227, 133, 0.1));
  color: var(--warning-color);
}

.degree-low {
  background: linear-gradient(135deg, rgba(243, 139, 168, 0.2), rgba(243, 139, 168, 0.1));
  color: var(--danger-color);
}

.summary-card {
  height: 100%;
}

.summary-title {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.summary-text {
  color: var(--text-primary);
  line-height: 1.8;
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

.list-container {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-container li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: var(--text-primary);
}

.skills-table {
  max-height: 400px;
  overflow-y: auto;
}

.compare-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.compare-item {
  padding: 12px;
  background-color: var(--bg-tertiary);
  border-radius: 8px;
}

.compare-name {
  color: var(--primary-color);
  font-weight: 500;
  margin-bottom: 6px;
}

.compare-evidence {
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background-color: var(--bg-tertiary);
  border-radius: 8px;
  color: var(--text-primary);
  line-height: 1.6;
}
</style>
