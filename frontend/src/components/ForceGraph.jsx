import { useEffect, useRef, useState } from 'react'
import * as echarts from 'echarts'

/**
 * 产业链力导向图谱 —— 防抖动三保险：
 * 1. 初始即隐藏：opacity 由 settling 状态驱动，首帧就是 0，隐藏态不设 transition（瞬时切换）
 * 2. 重跑布局前先【瞬时】隐藏画布再 setOption —— 力学模拟散开的初始帧永远不可见
 * 3. 高阻尼收敛约 3.2s 后才淡入，只呈现小范围缓慢漂移
 * 尺寸策略：根容器 absolute inset-0 填满父级（父级需 relative 且有确定高度，
 * 由父级/grid 行高决定），画布再铺满根容器——图例 bottom:0 恒等于模块底部。
 */
export default function ForceGraph({ nodes, links }) {
  const ref = useRef(null)
  const chartRef = useRef(null)
  const [settling, setSettling] = useState(true)

  useEffect(() => {
    if (!ref.current) return
    if (!nodes?.length) { setSettling(false); return }
    // StrictMode 下 effect 会 挂载→卸载→再挂载，因此每次都确保实例有效
    if (!chartRef.current || chartRef.current.isDisposed?.()) {
      chartRef.current = echarts.init(ref.current, 'dark')
    }
    const chart = chartRef.current

    // 关键：先“瞬时”隐藏（禁用过渡），再重启力学布局，
    // 消除淡出窗口期内可见的剧烈抖动画面
    const el = ref.current
    el.style.transition = 'none'
    el.style.opacity = '0'

    chart.setOption({
      animationDuration: 600,
      animationEasing: 'cubicOut',
      tooltip: {
        // 统一从 p.data 读原始数据（ECharts 5 边参数的 p.source/p.value 不稳定，会出现 undefined）
        formatter: p => {
          const d = p.data || {}
          if (p.dataType === 'node') {
            return `${d.name ?? p.name} 产出变动: ${d.value ?? 0}%`
          }
          const w = typeof d.value === 'number' ? d.value : 0
          return `${d.source ?? '?'} → ${d.target ?? '?'} 直接消耗系数: ${w}`
        },
      },
      legend: {
        data: ['冲击源（房地产/建筑）', '产业链部门'],
        bottom: 0, textStyle: { color: '#94a3b8', fontSize: 11 },
      },
      series: [{
        type: 'graph', layout: 'force', roam: true,
        top: 50, bottom: 70, left: 60, right: 60,  // 布局边界：留边距防贴边
        categories: [
          { name: '冲击源（房地产/建筑）', itemStyle: {
            color: { type: 'radial', x: 0.35, y: 0.35, r: 0.9,
              colorStops: [{ offset: 0, color: '#93c5fd' }, { offset: 1, color: '#2563eb' }] },
            shadowColor: 'rgba(59,130,246,0.5)', shadowBlur: 14 } },
          { name: '产业链部门', itemStyle: {
            color: { type: 'radial', x: 0.35, y: 0.35, r: 0.9,
              colorStops: [{ offset: 0, color: '#6ee7b7' }, { offset: 1, color: '#0d9488' }] },
            shadowColor: 'rgba(20,184,166,0.4)', shadowBlur: 10 } },
        ],
        force: {
          repulsion: 1600,     // 斥力较强，节点间距足够容纳下方标签
          edgeLength: [120, 230],  // 长连线，充分利用正方形画布
          gravity: 0.14,       // 向心力，收拢节点、防止飞出画布或沉底
          friction: 0.9,       // 高阻尼：收敛后只保留小范围缓慢漂移
          collide: 55,         // 节点碰撞半径（symbolSize 30~75 + 下方标签高约18px），
                               // 直接阻止节点与相邻节点（含标签区）重叠
        },
        // 标签放节点下方 + 深色描边光晕，避免亮底白字看不清
        label: { show: true, position: 'bottom', distance: 6, color: '#e2e8f0', fontSize: 11,
          textBorderColor: '#060a14', textBorderWidth: 3 },
        edgeLabel: { show: false },
        lineStyle: { color: '#475569', curveness: 0.15 },
        emphasis: { focus: 'adjacency', lineStyle: { width: 3 } },
        data: nodes.map(n => ({ ...n })),
        links,
      }],
    }, true)

    setSettling(true)

    // 收敛期间不可见，收敛完成后恢复过渡并淡入
    const timer = setTimeout(() => setSettling(false), 3200)

    // 容器尺寸随窗口/网格行高变化，需同步 resize 图表
    const ro = new ResizeObserver(() => chart.resize())
    ro.observe(el)
    const onResize = () => chart.resize()
    window.addEventListener('resize', onResize)
    return () => {
      clearTimeout(timer)
      ro.disconnect()
      window.removeEventListener('resize', onResize)
    }
  }, [nodes, links])

  useEffect(() => () => {
    chartRef.current?.dispose()
    chartRef.current = null  // 关键：清空引用，允许 StrictMode 二次挂载重新 init
  }, [])

  // 根容器铺满父级（父级需 relative 且有确定高度），画布再铺满根容器
  return (
    <div className="absolute inset-0">
      {settling && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 z-10">
          <div className="text-xs text-slate-500">图谱布局计算中…</div>
          <div className="loading-bar w-40" />
        </div>
      )}
      <div ref={ref} style={{
        position: 'absolute',
        inset: 0,
        opacity: settling ? 0 : 1,
        transition: settling ? 'none' : 'opacity .6s ease',
      }} />
    </div>
  )
}
