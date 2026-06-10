# Offer-Catcher — AI 智能职位匹配系统

让 AI 帮你找到梦想工作。上传简历，智能匹配顶级职位，获取由 AI 驱动的个性化简历优化报告。

## 功能概览

### 求职者端
- **AI 简历诊断** — 上传简历（PDF/Word/Excel/图片/TXT/Markdown），AI 提取关键信息并匹配职位库，生成完整的匹配度诊断报告
- **实时岗位抓取** — 根据简历内容自动从腾讯招聘等平台抓取实时岗位
- **JD 精准匹配** — 粘贴任意招聘平台的职位描述，AI 深度分析简历与 JD 的契合度，输出 Strengths→Gaps→优化建议→面试准备四段报告
- **简历优化** — 针对具体岗位给出可操作的简历修改建议
- **AI 简历润色** — 根据 JD 和你的背景，自动生成 STAR 法则扩写的定制简历草稿
- **HR 视角模拟** — 模拟大厂 HR 真实内心独白读简历，给出秒级初筛判断

### 招聘者端
- **发布岗位** — 填写职位需求，AI 润色生成专业 JD
- **批量简历筛选** — 三阶段 AI 推荐流水线：
  - **Stage A** 硬性条件筛选（提示词注入检测 / 必备技能 / 学历门槛）
  - **Stage B** LLM 5 维逐项评分（技能匹配 / 学历匹配 / 经验匹配 / 项目相关度 / 简历质量）
  - **Stage C** LLM 横向对比最终排名，输出录用建议

### 通用
- 中英文双语界面，语言偏好本地持久化
- 省份/城市/岗位类型多维度筛选
- 支持预设岗位 / 实时抓取 / 企业直招三种数据源

## API 端点

| 端点 | 说明 |
|------|------|
| `GET /health` | 健康检查 |
| `POST /api/match` | 简历匹配 + AI 诊断报告（SSE 流式） |
| `POST /api/analyze-jd` | JD 精准匹配分析（SSE 流式） |
| `POST /api/draft-resume` | AI 生成简历草稿（SSE 流式） |
| `POST /api/generate-jd` | AI 润色生成 JD |
| `GET /api/jobs/{id}/jd` | 获取完整 JD（懒加载 + 缓存） |
| `POST /api/jobs/{id}/optimize-resume` | 针对岗位优化简历（流式） |
| `POST /api/jobs/{id}/hr-view` | HR 视角模拟审阅简历（流式） |
| `POST /api/post-job` | 发布岗位 |
| `POST /api/batch-match` | 批量筛选 & 排名（SSE 流式） |

## 技术栈

| 层 | 技术 |
|----|------|
| 后端框架 | Python FastAPI |
| 前端框架 | Vue 3 + Vite |
| 国际化 | vue-i18n |
| LLM 调用 | Anthropic Messages API 格式（兼容 DeepSeek） |
| 文档解析 | PyMuPDF / python-docx / openpyxl / Tesseract OCR |
| 数据存储 | SQLite |
| 部署 | Render（免费层） |

## 快速开始

### 1. 环境准备

```bash
# Python 3.10+
pip install fastapi uvicorn httpx pymupdf python-docx openpyxl pillow python-dotenv pytesseract

# Node.js 18+
cd frontend && npm install
```

### 2. 配置 API Key

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 API Key：

```env
LLM_API_KEY=你的API密钥
LLM_BASE_URL=https://api.deepseek.com/anthropic
LLM_MODEL=deepseek-chat
```

支持的 LLM Base URL：
- `https://api.deepseek.com/anthropic` — Anthropic 格式
- `https://api.deepseek.com/v1` — OpenAI 兼容格式

### 3. 启动后端

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 启动前端

```bash
cd frontend
npm run dev
```

前端开发服务器默认运行在 `http://localhost:5173`，API 请求自动代理到 `http://localhost:8000`。

## 项目结构

```
AI_HR_project/
├── backend/
│   ├── main.py          # FastAPI 全栈后端（单文件）
│   └── data/
│       ├── seed_jobs.json   # 预设种子职位
│       └── company_colors.json  # 公司品牌色
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 主入口、路由控制
│   │   ├── i18n.js          # 国际化文案（中/英）
│   │   └── components/
│   │       ├── LandingPage.vue   # 求职者首页
│   │       ├── JdMatch.vue       # JD 精准匹配页
│   │       ├── BatchMatch.vue    # 批量筛选 HR 端
│   │       └── MyProfile.vue     # 个人中心
│   ├── index.html
│   └── vite.config.js
├── .env.example          # 环境变量模板
├── .gitignore
└── idea.md               # 批量筛选功能设计文档
```

## License

MIT
