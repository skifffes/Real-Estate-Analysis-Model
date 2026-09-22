import { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

export default function Chart({ option, height = 320 }) {
  const ref = useRef(null)
  const chart = useRef(null)
  const onResize = useRef(() => {})

  useEffect(() => {
    // StrictMode 下 effect 会 挂载→卸载→再挂载，因此每次都确保实例有效
    if ((!chart.current || chart.current.isDisposed?.()) && ref.current) {
      chart.current = echarts.init(ref.current, 'dark')
    }
    onResize.current = () => chart.current?.resize()
    window.addEventListener('resize', onResize.current)
    if (chart.current && option) chart.current.setOption(option, true)
    return () => window.removeEventListener('resize', onResize.current)
  }, [option])

  useEffect(() => () => {
    chart.current?.dispose()
    chart.current = null  // 关键：清空引用，允许 StrictMode 二次挂载时重新 init
  }, [])

  return <div ref={ref} style={{ height }} className="w-full" />
}
