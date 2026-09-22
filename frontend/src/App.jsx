import { NavLink, Route, Routes } from 'react-router-dom'
import Home from './pages/Home.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Upload from './pages/Upload.jsx'
import Reports from './pages/Reports.jsx'

const NAV = [
  { to: '/', label: '智能问答', desc: 'AI Agent 分析' },
  { to: '/dashboard', label: '风险仪表盘', desc: 'Dashboard' },
  { to: '/upload', label: '数据上传', desc: 'CSV / Excel' },
  { to: '/reports', label: '报告中心', desc: 'Markdown / PDF' },
]

export default function App() {
  return (
    <div className="flex h-screen">
      <aside className="no-print w-60 shrink-0 border-r border-slate-800 bg-slate-950 flex flex-col">
        <div className="p-5 border-b border-slate-800">
          <div className="text-blue-400 text-2xl font-bold leading-tight">RE Risk</div>
          <div className="text-slate-500 text-xs mt-1">房地产产业链风险<br />智能分析平台</div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {NAV.map(n => (
            <NavLink key={n.to} to={n.to} end={n.to === '/'}
              className={({ isActive }) =>
                `block px-4 py-2.5 rounded-lg transition ${isActive
                  ? 'bg-blue-600/20 text-blue-300 border border-blue-800'
                  : 'text-slate-400 hover:bg-slate-900 border border-transparent'}`}>
              <div className="text-sm font-medium">{n.label}</div>
              <div className="text-xs text-slate-500">{n.desc}</div>
            </NavLink>
          ))}
        </nav>
        <div className="p-4 text-xs text-slate-600 border-t border-slate-800">
          LLM Agent + RAG 知识库<br />投入产出模型 + 风险评分
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </main>
    </div>
  )
}
