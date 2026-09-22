import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getDashboard, riskColor } from '../api.js'
import Chart from '../components/Chart.jsx'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = () => getDashboard().then(setData).catch(e => setError(e.message))
    load()
    const t = setInterval(load, 8000)  // 轮询最新分析
    return () => clearInterval(t)
  }, [])

  if (error) return <div className="p-8 text-red-400">无法连接后端服务：{error}（请先启动 backend）</div>
  if (!data) return <div className="p-8 text-slate-500 animate-pulse">加载中…</div>

  const hasAnalysis = data.industry_impact?.length > 0

  return (
    <div className="p-8 space-y-6">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-xl font-bold">风险仪表盘</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {data.updated_at ? `最近分析：${data.updated_at}` : '暂无分析结果，请先在智能问答页提问'}
          </p>
        </div>
        <Link to="/" className="text-sm text-blue-400 hover:text-blue-300 no-print">去提问 →</Link>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Score 仪表盘 */}
        <div className="card">
          <div className="text-xs text-slate-500 mb-2">1. 综合风险评分</div>
          <Chart height={230} option={{
            series: [{
              type: 'gauge', startAngle: 210, endAngle: -30, min: 0, max: 100,
              progress: { show: true, width: 14, itemStyle: { color: riskColor(data.risk_level) } },
              axisLine: { lineStyle: { width: 14, color: [[1, '#1e293b']] } },
              axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false },
              pointer: { show: false }, anchor: { show: false },
              detail: { valueAnimation: true, fontSize: 40, offsetCenter: [0, '10%'],
                color: riskColor(data.risk_level),
                formatter: () => `{v|${data.risk_score ?? '-'}}\n{l|${data.risk_level}}`,
                rich: { v: { fontSize: 44, fontWeight: 'bold' }, l: { fontSize: 16, color: '#94a3b8', padding: [6, 0, 0, 0] } } },
              data: [{ value: data.risk_score || 0 }],
            }],
          }} />
        </div>

        {/* Industry Impact Chart */}
        <div className="card lg:col-span-2">
          <div className="text-xs text-slate-500 mb-2">2. 行业影响（产出变动%，投入产出模型）</div>
          {hasAnalysis ? <Chart option={{
            tooltip: { trigger: 'axis' },
            grid: { left: 90, right: 50, top: 10, bottom: 30 },
            xAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
            yAxis: { type: 'category', data: data.industry_impact.map(r => r.name).reverse() },
            series: [{
              type: 'bar',
              data: data.industry_impact.map(r => ({
                value: r.value,
                itemStyle: { color: r.value < 0 ? '#ef4444' : '#22c55e', borderRadius: 3 },
              })).reverse(),
              label: { show: true, position: 'right', formatter: '{c}%' },
              barMaxWidth: 22,
            }],
          }} /> : <Empty />}
        </div>

        {/* Supply Chain Graph */}
        <div className="card lg:col-span-2">
          <div className="text-xs text-slate-500 mb-2">3. 产业链传导图谱（连线=直接消耗系数≥0.03，节点大小=受冲击程度）</div>
          <Chart height={380} option={{
            tooltip: { formatter: p => p.dataType === 'node'
              ? `${p.name} 产出变动: ${p.value}%`
              : `${p.source} → ${p.target} 消耗系数: ${p.value}` },
            legend: { data: ['冲击源（房地产/建筑）', '产业链部门'], bottom: 0, textStyle: { color: '#94a3b8', fontSize: 11 } },
            series: [{
              type: 'graph', layout: 'force', roam: true,
              categories: [{ name: '冲击源（房地产/建筑）' }, { name: '产业链部门' }],
              force: { repulsion: 320, edgeLength: [70, 140] },
              label: { show: true, color: '#e2e8f0', fontSize: 11 },
              edgeLabel: { show: false },
              lineStyle: { color: '#475569', curveness: 0.15 },
              emphasis: { focus: 'adjacency', lineStyle: { width: 3 } },
              data: data.supply_chain.nodes.map(n => ({ ...n })),
              links: data.supply_chain.links,
            }],
          }} />
        </div>

        {/* Historical Comparison */}
        <div className="card">
          <div className="text-xs text-slate-500 mb-2">4. 历史对比（房地产投资 vs GDP 增速，%）</div>
          <Chart height={380} option={{
            tooltip: { trigger: 'axis' },
            legend: { data: ['房地产投资增速', 'GDP增速'], bottom: 0, textStyle: { color: '#94a3b8', fontSize: 11 } },
            grid: { left: 45, right: 15, top: 15, bottom: 60 },
            xAxis: { type: 'category', data: data.historical_comparison.years },
            yAxis: { type: 'value' },
            series: [
              { name: '房地产投资增速', type: 'line', smooth: true, symbolSize: 6,
                data: data.historical_comparison.re_investment_growth,
                lineStyle: { color: '#ef4444' }, itemStyle: { color: '#ef4444' },
                areaStyle: { color: 'rgba(239,68,68,0.08)' },
                markLine: { silent: true, data: [{ yAxis: 0 }], lineStyle: { color: '#64748b', type: 'dashed' } } },
              { name: 'GDP增速', type: 'line', smooth: true, symbolSize: 6,
                data: data.historical_comparison.gdp_growth,
                lineStyle: { color: '#38bdf8' }, itemStyle: { color: '#38bdf8' } },
            ],
          }} />
        </div>
      </div>

      {data.industry_scores?.length > 0 && (
        <div className="card">
          <div className="text-xs text-slate-500 mb-2">行业风险评分明细（收入30% + 债务30% + 现金流20% + 市场需求20%）</div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {data.industry_scores.map(s => (
              <div key={s.industry} className="bg-slate-950 rounded-lg p-3 border border-slate-800">
                <div className="text-xs text-slate-400">{s.industry}</div>
                <div className="text-2xl font-bold" style={{ color: riskColor(s.risk_level) }}>{s.risk_score}</div>
                <div className="text-xs" style={{ color: riskColor(s.risk_level) }}>{s.risk_level}风险</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

const Empty = () => (
  <div className="h-64 flex items-center justify-center text-slate-600 text-sm">
    暂无数据 —— 在「智能问答」输入 "分析房地产投资下降15%的影响" 后自动更新
  </div>
)
