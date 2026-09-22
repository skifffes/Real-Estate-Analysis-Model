import { useState } from 'react'
import { uploadFile, riskColor } from '../api.js'

export default function Upload() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const onFile = async (file) => {
    if (!file) return
    setLoading(true); setError(null); setResult(null)
    try {
      setResult(await uploadFile(file))
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  const risk = result?.risk_evaluation

  return (
    <div className="p-8 space-y-6 max-w-4xl">
      <header>
        <h1 className="text-xl font-bold">数据上传与分析</h1>
        <p className="text-xs text-slate-500 mt-0.5">支持 CSV / Excel，上传后自动进行统计分析与风险指标识别</p>
      </header>

      <div
        onDragOver={e => e.preventDefault()}
        onDrop={e => { e.preventDefault(); onFile(e.dataTransfer.files[0]) }}
        className="card border-dashed border-2 border-slate-700 text-center py-12 cursor-pointer hover:border-blue-600 transition"
        onClick={() => document.getElementById('fileInput').click()}>
        <input id="fileInput" type="file" accept=".csv,.xlsx,.xls" className="hidden"
          onChange={e => onFile(e.target.files[0])} />
        {loading ? <p className="text-blue-400 animate-pulse text-sm">正在分析数据…</p> : (
          <>
            <p className="text-slate-300 text-sm">拖拽文件到此处，或点击选择</p>
            <p className="text-slate-600 text-xs mt-1.5">
              建议包含指标列：收入同比、资产负债率、现金流变化、市场需求变化 —— 系统将自动计算风险评分
            </p>
          </>
        )}
      </div>

      {error && <div className="card border-red-900 text-red-400 text-sm">{error}</div>}

      {result && (
        <div className="card space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="font-medium text-blue-300">{result.filename}</h3>
            <span className="text-xs text-slate-500">{result.shape[0]} 行 × {result.shape[1]} 列 · file_id: {result.file_id}</span>
          </div>

          <p className="text-sm text-slate-300 bg-slate-950 rounded-lg p-3 border border-slate-800">{result.analysis_note}</p>

          {risk && (
            <div className="flex items-center gap-5 bg-slate-950 rounded-lg p-4 border border-slate-800">
              <div className="text-center">
                <div className="text-4xl font-bold" style={{ color: riskColor(risk.risk_level) }}>{risk.risk_score}</div>
                <div className="text-xs mt-1" style={{ color: riskColor(risk.risk_level) }}>{risk.risk_level}风险</div>
              </div>
              <div className="flex-1 grid grid-cols-2 gap-2 text-xs">
                {Object.entries(risk.components).map(([k, v]) => (
                  <div key={k}>
                    <div className="flex justify-between text-slate-400"><span>{k}</span><span>{v}</span></div>
                    <div className="h-1.5 bg-slate-800 rounded mt-1">
                      <div className="h-full bg-blue-500 rounded" style={{ width: `${v}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div>
            <div className="text-xs text-slate-500 mb-2">数值列统计摘要</div>
            <div className="overflow-auto">
              <table className="w-full text-xs">
                <thead><tr className="text-slate-500 border-b border-slate-800">
                  <th className="text-left py-1.5 pr-4">列名</th><th className="text-right px-3">均值</th>
                  <th className="text-right px-3">标准差</th><th className="text-right px-3">最小值</th>
                  <th className="text-right px-3">最大值</th><th className="text-right px-3">最新值</th>
                </tr></thead>
                <tbody>
                  {Object.entries(result.describe).map(([col, s]) => (
                    <tr key={col} className="border-b border-slate-800/50 text-slate-300">
                      <td className="py-1.5 pr-4">{col}</td>
                      <td className="text-right px-3">{s.mean}</td><td className="text-right px-3">{s.std}</td>
                      <td className="text-right px-3">{s.min}</td><td className="text-right px-3">{s.max}</td>
                      <td className="text-right px-3 text-blue-400">{s.latest ?? '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
