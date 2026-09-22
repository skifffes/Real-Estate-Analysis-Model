# 房地产产业链风险分析智能体
## Real Estate Supply Chain Risk Intelligence Agent

金融人工智能竞赛 Demo 系统 —— **大模型 Agent + 金融知识库 RAG + 投入产出产业链模型 + 风险评分** 的深度融合，而非普通聊天机器人。

---

## 一、系统架构

```
┌───────────────────────── Frontend (React + Vite + Tailwind + ECharts) ─────────────────────────┐
│  智能问答(结构化报告) │ 风险仪表盘(评分/影响/产业链图/历史对比) │ 数据上传 │ 报告中心(MD/PDF)    │
└────────────────────────────────────────────┬───────────────────────────────────────────────────┘
                                             │ REST API
┌────────────────────────────────────────────▼───────────────────────────────────────────────────┐
│                               Backend (Python FastAPI)                                          │
│  Agent Core: LLM Function Calling 循环（无 Key 时自动降级为规则引擎，Demo 永不翻车）             │
│  ├── Tool1 search_knowledge_base   → Chroma 向量库（论文/模型/政策/案例，关键词降级检索）        │
│  ├── Tool2 analyze_industry_chain  → 列昂惕夫投入产出模型 X=(I-A)⁻¹Y（14部门A矩阵）             │
│  ├── Tool3 compute_risk_score      → 多指标加权风险评分 0-100（收入/债务/现金流/需求）           │
│  ├── Tool4 retrieve_similar_cases  → 历史风险案例库（日本1990/美国2008/恒大2021/海南1992）       │
│  ├── Tool5 analyze_uploaded_data   → pandas 统计分析 + 指标识别                                 │
│  └── Tool6 get_dashboard_data      → 仪表盘数据组装                                             │
│  报告服务: 结构化 JSON → Markdown（持久化 backend/reports/）→ 前端导出 PDF                      │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 二、目录结构

```
backend/
  app/
    main.py               FastAPI 入口（chat/upload/dashboard/report/kb 接口）
    config.py             配置（LLM Key、目录）
    agent/core.py         Agent 核心：LLM 工具调用循环 + 规则引擎降级流水线
    agent/tools.py        6 个 Tool Schema（OpenAI Function Calling 格式）+ 执行分发
    knowledge/rag.py      RAG：文档切片 + Chroma 向量检索 + 关键词降级
    knowledge/documents/  金融知识库（投入产出原理/产业链结构/政策/案例/指标体系/传导机制）
    knowledge/cases.py    历史案例检索
    models/input_output.py  投入产出模型引擎（Leontief 逆矩阵、乘数、冲击测算、产业链图）
    models/risk.py        风险评分模型（行业评分 + 系统性综合评分）
    services/upload.py    CSV/Excel 自动分析（统计摘要 + 风险指标识别）
    services/report.py    Markdown 报告生成
    data/                 io_table.json(14部门) / cases.json / macro_history.json
  requirements.txt
  run.py
frontend/
  src/pages/              Home(问答) / Dashboard(仪表盘) / Upload(上传) / Reports(报告)
  src/components/Chart.jsx  ECharts 封装
testdata/                 演示用样本 CSV
```

## 三、运行方式

### 1. 后端

```powershell
cd backend
pip install -r requirements.txt
copy .env.example .env    # 填入 LLM_API_KEY（智谱/任意 OpenAI 兼容 API；不填则规则引擎降级运行）
python run.py             # http://localhost:8000  (文档: /docs)
```

### 2. 前端

```powershell
cd frontend
npm install
npm run dev               # http://localhost:5173
```

> 不配置 LLM_API_KEY 时系统自动降级为确定性规则分析流水线，所有模型测算、知识库检索、报告生成、Dashboard 均完整可用——保证比赛现场零依赖演示。

## 四、Demo 演示流程（比赛脚本，约 5 分钟）

| 步骤 | 操作 | 展示要点 |
|---|---|---|
| 1 | 打开首页，展示系统标题与建议问题 | 点明定位：非聊天机器人，而是"知识库+模型+Agent" |
| 2 | 提问 **"分析房地产投资下降15%的影响"** | Agent 自动调用：知识库检索 → 投入产出模型 → 风险评分 → 历史案例；展开"工具调用轨迹"证明 Function Calling |
| 3 | 指着返回报告逐区讲解 | 结构化输出：摘要/风险等级/影响行业/传导路径/模型依据/数据依据/关注指标 |
| 4 | 切换到 **Dashboard** | Risk Score 仪表盘、行业影响图、产业链传导图谱（力导向图）、历史对比曲线（8秒自动刷新） |
| 5 | 上传 `testdata/样本_房地产行业风险指标.csv` | 自动识别收入/负债率/现金流/需求列 → 实时风险评分 80+（极高风险） |
| 6 | 回到首页提问 "结合上传数据分析当前房地产行业风险" | Agent 调用 analyze_uploaded_data 融合数据 |
| 7 | 打开 **报告中心** | 六章结构 Markdown 报告 → 下载 .md / 导出 PDF |

### 备选演示问题
- 房价下跌20%会对哪些行业造成冲击？
- 房地产销售下滑对家电家具产业链的传导路径是什么？
- 当前房地产风险与2008年美国次贷危机有何异同？（触发历史案例检索）

## 五、与竞赛要求的对照

| 要求 | 实现 |
|---|---|
| LLM Agent + Function Calling | `agent/core.py` 工具调用循环，6 个工具，最多 8 轮规划 |
| 知识库 RAG（FAISS/Chroma） | Chroma 持久化向量库 + 6 篇金融文档切片 + 语义/关键词双检索 |
| Tool1 产业链影响（X=(I-A)⁻¹Y） | 14 部门 A 矩阵，直接/间接效应分解，乘数计算 |
| Tool2 风险评分 0-100 | 四指标加权模型 + 行业/系统性两级评分 |
| Tool3 历史案例检索 | 4 个结构化案例 + 相似度匹配 |
| 数据上传（CSV/Excel） | pandas 自动统计 + 风险指标列识别 + Agent 可调用 |
| Dashboard 四件套 | Risk Score 仪表盘 / 行业影响图 / 产业链图 / 历史对比 |
| 报告生成 MD/PDF | 六章结构 Markdown 持久化 + 浏览器导出 PDF |
| 本地可运行 | 纯本地依赖；LLM 可选，缺失时规则引擎降级 |

## 六、说明

- `app/data/io_table.json` 中的 A 矩阵基于中国 2018/2020 年投入产出表量级简化构建（14 部门），基准产出/最终需求为演示量级，比赛答辩时请说明"数据口径为简化 Demo 数据，模型框架可直接替换为统计局 42 部门真实投入产出表"。
- 知识库文档位于 `backend/app/knowledge/documents/`，可直接把参赛的两篇 PDF 论文（王国军 2004；满向昱等）文本化后放入该目录，重启即自动向量化入库。
