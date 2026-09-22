import { useEffect, useState } from 'react'
import { marked } from 'marked'
import { listReports, getReport } from '../api.js'

export default function Reports() {
  const [list, setList] = useState([])
  const [selected, setSelected] = useState(null)

  useEffect(() => { listReports().then(r => setList(r.items)).catch(() => {}) }, [])

  const open = async (rid) => {
    const r = await getReport(rid).catch(() => null)
    if (r) setSelected(r)
  }

  return (
    <div className="p-8 space-y-6">
      <header className="flex items-center justify-between no-print">
        <div>
          <h1 className="text-xl font-bold">报告中心</h1>
          <p className="text-xs text-slate-500 mt-0.5">结构化金融分析报告（Markdown 持久化 / 浏览器导出 PDF）</p>
        </div>
      </header>

      {list.length === 0 ? (
        <div className="card text-sm text-slate-500">暂无报告 —— 在「智能问答」完成一次分析后自动生成。</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="space-y-2 no-print">
            {list.map(r => (
              <button key={r.report_id} onClick={() => open(r.report_id)}
                className={`w-full text-left card p-3.5 transition hover:border-blue-700 ${selected?.report_id === r.report_id ? 'border-blue-600' : ''}`}>
                <div className="text-sm text-slate-200 truncate">{r.question || '未命名分析'}</div>
                <div className="text-xs text-slate-500 mt-1">
                  风险 {r.risk_score} · {r.risk_level} · {r.created_at}
                </div>
              </button>
            ))}
          </div>
          <div className="lg:col-span-3 card report-body" id="reportArea">
            {selected ? (
              <>
                <div className="flex gap-3 mb-4 no-print">
                  <a href={`http://localhost:8000/api/report/${selected.report_id}/download`}
                    className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200">下载 Markdown</a>
                  <button onClick={() => window.print()}
                    className="text-xs px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white">导出 PDF</button>
                </div>
                <div className="prose-sm text-slate-300 leading-7"
                  dangerouslySetInnerHTML={{ __html: marked.parse(_md(selected)) }} />
              </>
            ) : (
              <div className="text-sm text-slate-500 h-40 flex items-center justify-center">选择左侧报告查看</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// 前端直接渲染 Markdown（与后端生成的 backend/reports/{id}.md 同源同构）
function _md(report) {
  const rows = (report.affected_industries || []).map(r =>
    `| ${r.industry} | ${r.impact_pct}% | ${r.delta_output_yi} | ${r.risk_score ?? '-'} |`).join('\n')
  const scores = (report.industry_scores || []).map(s => `- **${s.industry}**：${s.risk_score}（${s.risk_level}）`).join('\n')
  const steps = (report.transmission_path || []).map((t, i) => `${i + 1}. ${t}`).join('\n')
  const basis = (report.data_basis || []).map(d => `- ${d}`).join('\n')
  const cases = (report.similar_cases || []).map(c => `- **${c.title}**：${c.peak_impact}`).join('\n')
  const kpis = (report.key_indicators || []).map(k => `- ${k}`).join('\n')
  return `# 房地产产业链风险分析报告

> 分析问题：**${report.question}**  
> 综合风险评分：**${report.risk_score} / 100（${report.risk_level}）**  
> 生成时间：${report.created_at}

## 1. Executive Summary
${report.summary}

## 2. Risk Assessment
${scores || '- ' + report.risk_level}

## 3. Transmission Mechanism（传导机制）
${steps}

## 4. Affected Industries（影响矩阵）

| 行业 | 产出变动% | 变动(亿元) | 风险评分 |
|---|---|---|---|
${rows}

${cases ? '### 历史对比\n' + cases : ''}
## 5. Model Explanation（模型依据）
${report.model_basis}

### 数据依据
${basis}

## 6. Conclusion（建议关注指标）
${kpis}

---
*本报告由房地产产业链风险分析智能体自动生成，仅供研究演示。*`
}
