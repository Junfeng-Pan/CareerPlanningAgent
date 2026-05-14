<template>
  <div class="match-result-container">
    <!-- 空状态 -->
    <el-empty
      v-if="!appStore.matchResult"
      description="请先进行岗位分析以获取匹配结果"
      :image-size="200"
    >
      <el-button type="primary" @click="$router.push('/job-analysis')">
        <el-icon><Briefcase /></el-icon>
        去分析岗位
      </el-button>
    </el-empty>

    <div v-else>
      <!-- 匹配度总览 -->
      <el-row :gutter="20" class="overview-row">
        <el-col :span="8">
          <el-card class="degree-card" shadow="hover">
            <div class="degree-content">
              <div class="degree-icon" :class="getDegreeClass(appStore.matchResult.summary?.matching_degree)">
                <el-icon :size="48"><TrendCharts /></el-icon>
              </div>
              <div class="degree-info">
                <div class="degree-label">匹配度</div>
                <div class="degree-value" :class="getDegreeClass(appStore.matchResult.summary?.matching_degree)">
                  {{ appStore.matchResult.summary?.matching_degree || '未知' }}
                </div>
              </div>
            </div>
            <el-progress
              :percentage="getDegreePercentage(appStore.matchResult.summary?.matching_degree)"
              :color="getDegreeColor(appStore.matchResult.summary?.matching_degree)"
              :stroke-width="8"
              :show-text="false"
              style="margin-top: 16px"
            />
          </el-card>
        </el-col>

        <el-col :span="16">
          <el-card class="summary-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span><el-icon><Document /></el-icon> 总体评价</span>
              </div>
            </template>
            <p class="summary-text">
              {{ appStore.matchResult.summary?.summary || '暂无总体评价' }}
            </p>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <!-- 左侧：匹配详情 -->
        <el-col :span="16">
          <!-- 优势分析 -->
          <el-card class="result-card" shadow="hover" v-if="appStore.matchResult.summary?.advantages?.length">
            <template #header>
              <div class="card-header success">
                <el-icon><CircleCheckFilled /></el-icon>
                <span>您的优势</span>
              </div>
            </template>
            <el-tag
              v-for="(advantage, index) in appStore.matchResult.summary.advantages"
              :key="index"
              type="success"
              effect="plain"
              style="margin: 4px"
            >
              <el-icon><Check /></el-icon>
              {{ advantage }}
            </el-tag>
          </el-card>

          <!-- 差距分析 -->
          <el-card class="result-card" shadow="hover" v-if="appStore.matchResult.summary?.gaps?.length">
            <template #header>
              <div class="card-header warning">
                <el-icon><WarningFilled /></el-icon>
                <span>需要提升的方面</span>
              </div>
            </template>
            <el-tag
              v-for="(gap, index) in appStore.matchResult.summary.gaps"
              :key="index"
              type="warning"
              effect="plain"
              style="margin: 4px"
            >
              <el-icon><Close /></el-icon>
              {{ gap }}
            </el-tag>
          </el-card>

          <!-- 技能匹配详情 -->
          <el-card class="result-card" shadow="hover" v-if="appStore.matchResult.skills?.length">
            <template #header>
              <div class="card-header">
                <span><el-icon><DataAnalysis /></el-icon> 技能匹配详情</span>
              </div>
            </template>

            <el-table :data="appStore.matchResult.skills" style="width: 100%">
              <el-table-column prop="name" label="技能名称" width="180" />
              <el-table-column label="匹配状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === '具备' ? 'success' : 'danger'" size="small">
                    <el-icon :is="row.status === '具备' ? 'Check' : 'Close'" />
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="证据/差距分析" min-width="300">
                <template #default="{ row }">
                  <el-popover placement="top" :width="350" trigger="hover">
                    <template #reference>
                      <span class="evidence-text">
                        {{ row.evidence || row.gap_analysis || '无' }}
                      </span>
                    </template>
                    <div style="font-size: 13px; line-height: 1.6">
                      <strong>{{ row.evidence ? '具备证据:' : '差距分析:' }}</strong><br>
                      {{ row.evidence || row.gap_analysis }}
                    </div>
                  </el-popover>
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <!-- 门槛要求匹配 -->
          <el-card class="result-card" shadow="hover" v-if="appStore.matchResult.thresholds?.length">
            <template #header>
              <div class="card-header">
                <span><el-icon><Document /></el-icon> 门槛要求匹配</span>
              </div>
            </template>

            <el-table :data="appStore.matchResult.thresholds" style="width: 100%">
              <el-table-column prop="name" label="要求" width="150" />
              <el-table-column label="匹配状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === '具备' ? 'success' : 'warning'" size="small">
                    {{ row.status || '待确认' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="evidence" label="证据" min-width="250" />
            </el-table>
          </el-card>

          <!-- 职业素养匹配 -->
          <el-card class="result-card" shadow="hover" v-if="appStore.matchResult.professionalism?.length">
            <template #header>
              <div class="card-header">
                <span><el-icon><Star /></el-icon> 职业素养匹配</span>
              </div>
            </template>

            <el-table :data="appStore.matchResult.professionalism" style="width: 100%">
              <el-table-column prop="name" label="素养要求" width="200" />
              <el-table-column label="匹配状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === '具备' ? 'success' : 'info'" size="small">
                    {{ row.status || '待评估' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="evidence" label="评估依据" min-width="250" />
            </el-table>
          </el-card>
        </el-col>

        <!-- 右侧：建议和图表 -->
        <el-col :span="8">
          <!-- 匹配度仪表图 -->
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span><el-icon><PieChart /></el-icon> 匹配度分析</span>
              </div>
            </template>
            <div ref="gaugeChartRef" class="echarts-chart gauge-chart"></div>
          </el-card>

          <!-- 技能匹配饼图 -->
          <el-card class="chart-card" shadow="hover" v-if="appStore.matchResult.skills?.length">
            <template #header>
              <div class="card-header">
                <span><el-icon><PieChart /></el-icon> 技能匹配分布</span>
              </div>
            </template>
            <div ref="pieChartRef" class="echarts-chart pie-chart"></div>
          </el-card>

          <!-- 推荐建议 -->
          <el-card class="suggestion-card" shadow="hover" v-if="appStore.matchResult.recommendations?.length">
            <template #header>
              <div class="card-header">
                <span><el-icon><Lightbulb /></el-icon> 发展建议</span>
              </div>
            </template>

            <el-timeline>
              <el-timeline-item
                v-for="(rec, index) in appStore.matchResult.recommendations"
                :key="index"
                :timestamp="`建议 ${index + 1}`"
                placement="top"
                color="#E6A23C"
              >
                <div class="suggestion-item">{{ rec }}</div>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { watch, nextTick, onMounted, ref } from 'vue'
import { useAppStore } from '@/store/app'
import * as echarts from 'echarts'

const appStore = useAppStore()
const gaugeChartRef = ref(null)
const pieChartRef = ref(null)
let gaugeChart = null
let pieChart = null

// 获取匹配度等级类名
const getDegreeClass = (degree) => {
  const classes = { '高': 'high', '中': 'medium', '低': 'low' }
  return classes[degree] || ''
}

// 获取匹配度百分比
const getDegreePercentage = (degree) => {
  const percentages = { '高': 90, '中': 60, '低': 30 }
  return percentages[degree] || 50
}

// 获取匹配度颜色
const getDegreeColor = (degree) => {
  const colors = { '高': '#67C23A', '中': '#E6A23C', '低': '#F56C6C' }
  return colors[degree] || '#909399'
}

// 初始化仪表图
const initGaugeChart = () => {
  if (!gaugeChartRef.value || !appStore.matchResult) return

  gaugeChart = echarts.init(gaugeChartRef.value)
  const percentage = getDegreePercentage(appStore.matchResult.summary?.matching_degree)
  const color = getDegreeColor(appStore.matchResult.summary?.matching_degree)

  const option = {
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      splitNumber: 5,
      radius: '90%',
      center: ['50%', '60%'],
      itemStyle: { color },
      progress: {
        show: true,
        width: 18
      },
      pointer: { show: false },
      axisLine: {
        lineStyle: {
          width: 18,
          color: [[1, '#eee']]
        }
      },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      title: { show: false },
      detail: {
        valueAnimation: true,
        width: '60%',
        lineHeight: 40,
        depth: 40,
        offsetCenter: [0, '0%'],
        fontSize: 30,
        fontWeight: 'bolder',
        formatter: '{value}%',
        color: 'auto'
      }
    }]
  }

  gaugeChart.setOption({ series: [{ data: [{ value: percentage }] }] })

  window.addEventListener('resize', () => gaugeChart && gaugeChart.resize())
}

// 初始化饼图
const initPieChart = () => {
  if (!pieChartRef.value || !appStore.matchResult.skills?.length) return

  pieChart = echarts.init(pieChartRef.value)

  const skills = appStore.matchResult.skills
  const matched = skills.filter(s => s.status === '具备').length
  const unmatched = skills.length - matched

  const option = {
    tooltip: { trigger: 'item' },
    legend: {
      orient: 'horizontal',
      bottom: '0%',
      left: 'center'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: { show: false },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      data: [
        { value: matched, name: '已具备', itemStyle: { color: '#67C23A' } },
        { value: unmatched, name: '待提升', itemStyle: { color: '#F56C6C' } }
      ]
    }]
  }

  pieChart.setOption(option)
  window.addEventListener('resize', () => pieChart && pieChart.resize())
}

watch(() => appStore.matchResult, () => {
  nextTick(() => {
    initGaugeChart()
    initPieChart()
  })
}, { immediate: true })

onMounted(() => {
  if (!appStore.matchResult) {
    appStore.fetchMatchResult()
  }
})
</script>

<style scoped lang="scss">
.match-result-container {
  max-width: 1400px;
  margin: 0 auto;
}

.overview-row {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;

  &.success {
    color: #67C23A;
  }

  &.warning {
    color: #E6A23C;
  }
}

.degree-card {
  .degree-content {
    display: flex;
    align-items: center;
    gap: 16px;

    .degree-icon {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;

      &.high {
        background: linear-gradient(135deg, #67C23A 0%, #52c41a 100%);
        color: #fff;
      }

      &.medium {
        background: linear-gradient(135deg, #E6A23C 0%, #e6a23c 100%);
        color: #fff;
      }

      &.low {
        background: linear-gradient(135deg, #F56C6C 0%, #f56c6c 100%);
        color: #fff;
      }
    }

    .degree-info {
      flex: 1;

      .degree-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 4px;
      }

      .degree-value {
        font-size: 28px;
        font-weight: bold;

        &.high { color: #67C23A; }
        &.medium { color: #E6A23C; }
        &.low { color: #F56C6C; }
      }
    }
  }
}

.summary-card {
  .summary-text {
    margin: 0;
    font-size: 15px;
    line-height: 1.8;
    color: #606266;
  }
}

.result-card {
  margin-bottom: 20px;

  :deep(.el-tag) {
    margin-right: 8px;
    margin-bottom: 8px !important;
  }

  .evidence-text {
    color: #606266;
    font-size: 13px;
    cursor: pointer;

    &:hover {
      color: #409EFF;
    }
  }
}

.chart-card {
  margin-bottom: 20px;

  .echarts-chart {
    width: 100%;
  }

  .gauge-chart {
    height: 200px;
  }

  .pie-chart {
    height: 250px;
  }
}

.suggestion-card {
  :deep(.el-timeline-item__content) {
    .suggestion-item {
      font-size: 14px;
      color: #606266;
      line-height: 1.6;
      background: #fdf6ec;
      padding: 12px;
      border-radius: 8px;
    }
  }
}
</style>
