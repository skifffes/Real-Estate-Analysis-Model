import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { chat, riskColor, getHealth } from '../api.js'
import Chart from '../components/Chart.jsx'

const SUGGESTIONS = [
  '分析房地产投资下降15%的影响',
  '房价下跌20%会对哪些行业造成冲击？',
  '房地产销售下滑对家电家具产业链的传导路径',
]

export default function Home() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [health, setHealth] = useState(null)

  useEffect(() => { getHealth().then(setHealth).catch(() => {}) }, [])

  const send = async (q) => {
    const question = q || input
    if (!question.trim() || loading) return
    setInput('')
    setMessages(m => [...m, { role: 'user', text: question }])
    setLoading(true)
    try {
      const report = await chat(question)
      setMessages(m => [...m, { role: 'ai', report }])
    } catch (e) {
      setMessages(m => [...m, { role: 'ai', error: e.response?.data?.detail || e.message }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full flex flex-col">
      <header className="px-8 py-5 border-b border-slate-800 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100">房地产产业链风险智能分析</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Agent 模式：{health?.agent_mode || '检测中…'} · 回答自动调用知识库 / 投入产出模型 / 风险评分 / 历史案例工具
          </p>
        </div>
        <Link to="/dashboard" className="text-sm text-blue-400 hover:text-blue-300">查看 Dashboard →</Link>
      </header>

      <div className="flex-1 overflow-auto px-8 py-6 space-y-5 max-w-4xl w-full mx-auto">
        {messages.length === 0 && (
          <div className="card">
            <p className="text-slate-300 text-sm leading-7">
              输入房地产相关问题（如冲击情景），智能体将自动规划并调用
              <span className="text-blue-400"> 知识库检索 </span>/
              <span className="text-blue-400"> 投入产出模型 </span>/
              <span className="text-blue-400"> 风险评分 </span>/
              <span className="text-blue-400"> 历史案例 </span>
              工具，生成结构化风险分析报告。
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {SUGGESTIONS.map(s => (
                <button key={s} onClick={() => send(s)}
                  className="text-xs px-3 py-1.5 rounded-full border border-slate-700 text-slate-300 hover:border-blue-600 hover:text-blue-300">
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => m.role === 'user' ? (
          <div key={i} className="flex justify-end">
            <div className="bg-blue-600 rounded-2xl rounded-br-sm px-4 py-2.5 max-w-xl text-sm">{m.text}</div>
          </div>
        ) : (
          <div key={i} className="flex justify-start">
            {m.error ? <div className="card border-red-900 text-red-400 text-sm">{m.error}</div>
                     : <ReportView report={m.report} />}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="card text-sm text-slate-400 animate-pulse">
              Agent 正在规划工具调用（知识库检索 → 投入产出模型测算 → 风险评分 → 案例对比）…
            </div>
          </div>
        )}
      </div>

      <footer className="px-8 pb-6 max-w-4xl w-full mx-auto">
        <div className="flex gap-3">
          <input value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && send()}
            placeholder="输入问题，例如：分析房地产投资下降15%的影响"
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm focus:border-blue-600 outline-none" />
          <button onClick={() => send()} disabled={loading}
            className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-xl px-6 text-sm font-medium">
            分析
          </button>
        </div>
      </footer>
    </div>
  )
}

function ReportView({ report }) {
  const { summary, risk_level, risk_score, affected_industries, industry_scores,
          transmission_path, model_basis, data_basis, key_indicators, similar_cases, tool_trace, agent_mode } = report
  const impactChart = affected_industries?.length ? {
    tooltip: { trigger: 'axis' },
    grid: { left: 80, right: 30, top: 10, bottom: 30 },
    xAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
    yAxis: { type: 'category', data: affected_industries.map(r => r.industry).reverse() },
    series: [{
      type: 'bar',
      data: affected_industries.map(r => ({ value: r.impact_pct, itemStyle: { color: r.impact_pct < 0 ? '#ef4444' : '#22c55e' } })).reverse(),
      label: { show: true, position: 'right', formatter: '{c}%' },
    }],
  } : null

  return (
    <div className="card max-w-3xl w-full space-y-5">
      <div className="flex items-start justify-between gap-4">
        <h3 className="text-blue-300 font-semibold">产业链风险分析报告</h3>
        <div className="text-right shrink-0">
          <span className="text-2xl font-bold" style={{ color: riskColor(risk_level) }}>{risk_score ?? '-'}</span>
          <span className="text-xs text-slate-500"> / 100 · </span>
          <span className="px-2 py-0.5 rounded text-xs font-medium"
            style={{ background: riskColor(risk_level) + '25', color: riskColor(risk_level) }}>{risk_level}</span>
        </div>
      </div>

      <p className="text-sm text-slate-300 leading-7">{summary}</p>

      {impactChart && (
        <div>
          <div className="text-xs text-slate-500 mb-1">行业影响（产出变动%，投入产出模型测算）</div>
          <Chart option={impactChart} height={260} />
        </div>
      )}

      <div>
        <div className="text-xs text-slate-500 mb-2">风险传导路径</div>
        <div className="space-y-1.5">
          {transmission_path?.map((t, i) => (
            <div key={i} className="flex items-start gap-2 text-sm">
              <span className="w-5 h-5 shrink-0 rounded-full bg-slate-800 border border-slate-700 text-xs flex items-center justify-center text-blue-400">{i + 1}</span>
              <span className="text-slate-300">{t}</span>
            </div>
          ))}
        </div>
      </div>

      {industry_scores?.length > 0 && (
        <div>
          <div className="text-xs text-slate-500 mb-2">行业风险评分（多指标加权模型）</div>
          <div className="flex flex-wrap gap-2">
            {industry_scores.map(s => (
              <span key={s.industry} className="text-xs px-2.5 py-1 rounded-md border border-slate-700"
                style={{ color: riskColor(s.risk_level) }}>
                {s.industry} {s.risk_score} · {s.risk_level}
              </span>
            ))}
          </div>
        </div>
      )}

      {similar_cases?.length > 0 && (
        <div>
          <div className="text-xs text-slate-500 mb-2">历史案例对比</div>
          {similar_cases.map((c, i) => (
            <div key={i} className="text-xs text-slate-400 border-l-2 border-amber-700 pl-3 py-1">
              <span className="text-amber-400">{c.title}</span>：{c.peak_impact} <span className="text-slate-500">— {c.lessons}</span>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div>
          <div className="text-slate-500 mb-1">模型依据</div>
          <p className="text-slate-300 leading-6">{model_basis}</p>
        </div>
        <div>
          <div className="text-slate-500 mb-1">数据依据（知识库检索）</div>
          <ul className="text-slate-400 space-y-1">
            {data_basis?.map((d, i) => <li key={i}>· {d}</li>)}
          </ul>
        </div>
      </div>

      <div>
        <div className="text-xs text-slate-500 mb-1.5">建议关注指标</div>
        <div className="flex flex-wrap gap-1.5">
          {key_indicators?.map(k => (
            <span key={k} className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">{k}</span>
          ))}
        </div>
      </div>

      {tool_trace?.length > 0 && (
        <details className="text-xs text-slate-500">
          <summary className="cursor-pointer hover:text-slate-300">Agent 工具调用轨迹（{tool_trace.length} 次）· 模式：{agent_mode}</summary>
          <div className="mt-2 space-y-1 font-mono">
            {tool_trace.map((t, i) => (
              <div key={i} className="bg-slate-950 rounded p-2">
                <span className="text-blue-400">{t.tool}</span>({JSON.stringify(t.args)}) → {t.result_preview}
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
