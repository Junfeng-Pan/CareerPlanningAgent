<template>
  <div class="match-result-detail">
    <!-- 匹配度总览 -->
    <div class="overview-section">
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="degree-gauge">
            <div ref="gaugeChartRef" class="gauge-chart"></div>
            <div class="degree-label">
              匹配度：<span :class="getDegreeClass(result?.summary?.matching_degree)">
                {{ result?.summary?.matching_degree || '未知' }}
              </span>
            </div>
          </div>
        </el-col>

        <el-col :span="16">
          <el-card class="summary-card" shadow="hover">
            <div class="summary-content">
              <h3>总体评价</h3>
              <p>{{ result?.summary?.summary || '暂无评价' }}</p>
            </div>
          </el-card>

          <div class="analysis-section" v-if="result?.summary?.advantages?.length || result?.summary?.gaps?.length">
            <div class="analysis-card advantages" v-if="result?.summary?.advantages?.length">
              <div class="card-header">
                <el-icon class="icon-success"><CircleCheckFilled /></el-icon>
                <span>您的优势</span>
              </div>
              <div class="tags">
                <el-tag
                  v-for="(adv, index) in result.summary.advantages"
                  :key="index"
                  type="success"
                  effect="plain"
                  style="margin: 4px"
                >
                  {{ adv }}
                </el-tag>
              </div>
            </div>

            <div class="analysis-card gaps" v-if="result?.summary?.gaps?.length">
              <div class="card-header">
                <el-icon class="icon-warning"><WarningFilled /></el-icon>
                <span>需要提升</span>
              </div>
              <div class="tags">
                <el-tag
                  v-for="(gap, index) in result.summary.gaps"
                  :key="index"
                  type="warning"
                  effect="plain"
                  style="margin: 4px"
                >
                  {{ gap }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 技能匹配饼图 -->
    <div class="charts-row" v-if="result?.skills?.length">
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="chart-card">
            <h3>技能匹配分布</h3>
            <div ref="pieChartRef" class="pie-chart"></div>
          </div>
        </el-col>

        <el-col :span="12">
          <div class="chart-card">
            <h3>详细建议</h3>
            <el-timeline class="suggestion-timeline">
              <el-timeline-item
                v-for="(rec, index) in result.recommendations"
                :key="index"
                :timestamp="`建议 ${index + 1}`"
                placement="top"
                color="#E6A23C"
              >
                <div class="suggestion-item">{{ rec }}</div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 技能匹配详情表格 -->
    <div class="detail-section" v-if="result?.skills?.length">
      <h3><el-icon><DataAnalysis /></el-icon> 技能匹配详情</h3>
      <el-table :data="result.skills" style="width: 100%" :default-sort="{prop: 'status', order: 'ascending'}">
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
    </div>

    <!-- 门槛要求匹配 -->
    <div class="detail-section" v-if="result?.thresholds?.length">
      <h3><el-icon><Document /></el-icon> 门槛要求匹配</h3>
      <el-table :data="result.thresholds" style="width: 100%">
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
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  result: Object
})

const gaugeChartRef = ref(null)
const pieChartRef = ref(null)
let gaugeChart = null
let pieChart = null

const getDegreeClass = (degree) => {
  const classes = { '高': 'high', '中': 'medium', '低': 'low' }
  return classes[degree] || ''
}

const getDegreePercentage = (degree) => {
  const percentages = { '高': 90, '中': 60, '低': 30 }
  return percentages[degree] || 50
}

const initGaugeChart = () => {
  if (!gaugeChartRef.value || !props.result) return

  gaugeChart = echarts.init(gaugeChartRef.value)
  const percentage = getDegreePercentage(props.result.summary?.matching_degree)
  const colorMap = { '高': '#67C23A', '中': '#E6A23C', '低': '#F56C6C' }
  const color = colorMap[props.result.summary?.matching_degree] || '#909399'

  const option = {
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      radius: '90%',
      center: ['50%', '60%'],
      itemStyle: { color },
      progress: { show: true, width: 18 },
      pointer: { show: false },
      axisLine: { lineStyle: { width: 18, color: [[1, '#eee']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      title: { show: false },
      detail: {
        valueAnimation: true,
        fontSize: 30,
        fontWeight: 'bold',
        formatter: '{value}%',
        offsetCenter: [0, '0%'],
        color: 'auto'
      }
    }]
  }

  gaugeChart.setOption({ series: [{ data: [{ value: percentage }] }] })
  window.addEventListener('resize', () => gaugeChart && gaugeChart.resize())
}

const initPieChart = () => {
  if (!pieChartRef.value || !props.result?.skills?.length) return

  pieChart = echarts.init(pieChartRef.value)

  const skills = props.result.skills
  const matched = skills.filter(s => s.status === '具备').length
  const unmatched = skills.length - matched

  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'horizontal', bottom: '0%', left: 'center' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
      data: [
        { value: matched, name: '已具备', itemStyle: { color: '#67C23A' } },
        { value: unmatched, name: '待提升', itemStyle: { color: '#F56C6C' } }
      ]
    }]
  }

  pieChart.setOption(option)
  window.addEventListener('resize', () => pieChart && pieChart.resize())
}

watch(() => props.result, () => {
  nextTick(() => {
    initGaugeChart()
    initPieChart()
  })
}, { immediate: true })
</script>

<style scoped lang="scss">
.match-result-detail {
  .overview-section {
    margin-bottom: 20px;

    .degree-gauge {
      background: #fff;
      padding: 20px;
      border-radius: 12px;
      text-align: center;

      .gauge-chart {
        height: 180px;
        width: 100%;
      }

      .degree-label {
        margin-top: 10px;
        font-size: 16px;
        color: #606266;

        span {
          font-weight: bold;
          font-size: 24px;

          &.high { color: #67C23A; }
          &.medium { color: #E6A23C; }
          &.low { color: #F56C6C; }
        }
      }
    }

    .summary-card {
      margin-bottom: 16px;

      .summary-content {
        h3 {
          margin: 0 0 12px 0;
          font-size: 15px;
          color: #303133;
        }

        p {
          margin: 0;
          font-size: 14px;
          line-height: 1.8;
          color: #606266;
        }
      }
    }

    .analysis-section {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;

      .analysis-card {
        background: #fff;
        padding: 16px;
        border-radius: 12px;

        .card-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 600;
          margin-bottom: 12px;

          .icon-success { color: #67C23A; }
          .icon-warning { color: #E6A23C; }
        }

        .tags {
          display: flex;
          flex-wrap: wrap;
        }
      }
    }
  }

  .charts-row {
    margin-bottom: 20px;

    .chart-card {
      background: #fff;
      padding: 20px;
      border-radius: 12px;

      h3 {
        margin: 0 0 16px 0;
        font-size: 16px;
        color: #303133;
      }

      .pie-chart {
        height: 250px;
        width: 100%;
      }

      .suggestion-timeline {
        :deep(.el-timeline-item__content) {
          .suggestion-item {
            background: #fdf6ec;
            padding: 10px;
            border-radius: 8px;
            font-size: 13px;
            color: #606266;
            line-height: 1.6;
          }
        }
      }
    }
  }

  .detail-section {
    background: #fff;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;

    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 16px 0;
      font-size: 16px;
      color: #303133;
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
}
</style>
