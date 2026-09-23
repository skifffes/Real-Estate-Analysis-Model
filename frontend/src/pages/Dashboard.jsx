import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getDashboard, riskColor } from '../api.js'
import Chart from '../components/Chart.jsx'
import ForceGraph from '../components/ForceGraph.jsx'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    // 数据未变化时返回原引用，避免 8 秒轮询触发图表重渲染（图谱节点跳位置）
    const load = () => getDashboard()
      .then(d => setData(prev => JSON.stringify(prev) === JSON.stringify(d) ? prev : d))
      .catch(e => setError(e.message))
    load()
    const t = setInterval(load, 8000)  // 轮询最新分析
    return () => clearInterval(t)
  }, [])

  if (error) return (
    <div className="p-8">
      <div className="card !border-red-900/70 text-red-400 text-sm max-w-xl">
        无法连接后端服务：{error}（请先启动 backend）
      </div>
    </div>
  )
  if (!data) return (
    <div className="p-8 space-y-4 max-w-3xl">
      <div className="h-8 w-48 rounded-lg bg-slate-800/60 animate-pulse" />
      <div className="grid grid-cols-3 gap-6">
        {[0, 1, 2].map(i => <div key={i} className="h-64 rounded-2xl bg-slate-900/60 border border-slate-800/60 animate-pulse" />)}
      </div>
    </div>
  )

  const hasAnalysis = data.industry_impact?.length > 0
  const color = riskColor(data.risk_level)

  return (
    <div className="p-8 space-y-6">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight">风险仪表盘</h1>
          <div className="flex items-center gap-2 mt-1">
            <span className="glow-dot" />
            <p className="text-xs text-slate-500">
              {data.updated_at ? `最近分析：${data.updated_at} · 每 8 秒自动刷新` : '暂无分析结果，请先在智能问答页提问'}
            </p>
          </div>
        </div>
        <Link to="/"
          className="text-sm px-4 py-2 rounded-lg border border-slate-700 text-slate-300 hover:border-blue-500/60 hover:text-blue-300 hover:bg-blue-600/10 transition-all no-print">
          去提问 →
        </Link>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Score 仪表盘 */}
        <div className="card card-hover anim-fade-up">
          <div className="section-label mb-2">综合风险评分</div>
          <Chart height={230} option={{
            series: [{
              type: 'gauge', startAngle: 210, endAngle: -30, min: 0, max: 100,
              progress: { show: true, width: 14, itemStyle: { color, shadowColor: color, shadowBlur: 14 } },
              axisLine: { lineStyle: { width: 14, color: [[1, '#1e293b']] } },
              axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false },
              pointer: { show: false }, anchor: { show: false },
              detail: { valueAnimation: true, fontSize: 40, offsetCenter: [0, '10%'],
                color,
                formatter: () => `{v|${data.risk_score ?? '-'}}\n{l|${data.risk_level}}`,
                rich: { v: { fontSize: 44, fontWeight: 'bold' }, l: { fontSize: 16, color: '#94a3b8', padding: [6, 0, 0, 0] } } },
              data: [{ value: data.risk_score || 0 }],
            }],
          }} />
        </div>

        {/* Industry Impact Chart */}
        <div className="card card-hover lg:col-span-2 anim-fade-up">
          <div className="section-label mb-2">行业影响（产出变动%，投入产出模型）</div>
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

        {/* Supply Chain Graph —— 2/3宽；高度与右侧列（grid行高）一致，画布填满卡片 */}
        <div className="card card-hover lg:col-span-2 anim-fade-up flex flex-col">
          <div className="section-label mb-2">产业链传导图谱（连线=直接消耗系数≥0.03，节点大小=受冲击程度）</div>
          <div className="flex-1 relative min-h-[480px]">
            <ForceGraph nodes={data.supply_chain.nodes} links={data.supply_chain.links} />
          </div>
        </div>

        {/* 右侧 1/3 列：历史对比 + 案例对标 上下堆叠，与左侧图谱等高 */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <div className="card card-hover anim-fade-up flex-1">
            <div className="section-label mb-2">历史对比（房地产投资 vs GDP 增速，%）</div>
            <Chart height={260} option={{
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

          <div className="card card-hover anim-fade-up">
            <div className="section-label mb-3">历史案例对标</div>
            {data.similar_cases?.length ? (
              <div className="space-y-3">
                {data.similar_cases.map((c, i) => (
                  <div key={i} className="border-l-2 border-amber-600/70 pl-3 py-0.5">
                    <div className="text-sm font-medium text-amber-300/90">{c.title}</div>
                    <div className="text-xs text-slate-400 mt-1 leading-5">{c.peak_impact}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-xs text-slate-600 py-4 text-center">完成一次冲击分析后自动对标历史案例</div>
            )}
          </div>

          <div className="card card-hover anim-fade-up flex-1">
            <div className="section-label mb-3">建议关注指标</div>
            {data.key_indicators?.length ? (
              <div className="flex flex-wrap gap-2 content-start">
                {data.key_indicators.map(k => (
                  <span key={k} className="text-xs px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700/70 text-slate-300">
                    {k}
                  </span>
                ))}
              </div>
            ) : (
              <div className="text-xs text-slate-600 py-4 text-center">完成一次冲击分析后自动生成监测清单</div>
            )}
          </div>
        </div>
      </div>

      {data.industry_scores?.length > 0 && (
        <div className="card anim-fade-up lg:col-span-3">
          <div className="section-label mb-3">行业风险评分明细（收入30% + 债务30% + 现金流20% + 市场需求20%）</div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {data.industry_scores.map(s => {
              const c = riskColor(s.risk_level)
              return (
                <div key={s.industry}
                  className="bg-slate-950/60 rounded-xl p-3.5 border border-slate-800/70 hover:border-slate-600 transition-colors">
                  <div className="text-xs text-slate-400">{s.industry}</div>
                  <div className="text-2xl font-extrabold mt-1" style={{ color: c }}>{s.risk_score}</div>
                  <div className="mt-2 h-1 rounded-full bg-slate-800 overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-500" style={{ width: `${s.risk_score}%`, background: c }} />
                  </div>
                  <div className="text-[11px] mt-1.5" style={{ color: c }}>{s.risk_level}风险</div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

const Empty = () => (
  <div className="h-64 flex flex-col items-center justify-center gap-3 text-slate-600 text-sm">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" className="w-10 h-10 opacity-50">
      <path d="M3 13h4v8H3zM10 9h4v12h-4zM17 5h4v16h-4z" />
    </svg>
    暂无数据 —— 在「智能问答」输入 "分析房地产投资下降15%的影响" 后自动更新
  </div>
)
