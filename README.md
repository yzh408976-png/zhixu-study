# 云帆 · AI 学习领航引擎

> **让每一次自习室里的埋头，都被科学看见。**

「云帆」是参赛作品，基于认知科学与动机心理学的研究证据，结合 AI 个性化诊断，
为期末、考研、考公、教资、法考、软考、四六级等备考场景生成有据可查的每日任务编排，
同时提供情绪守卫、12355 心理援助转介、考试节点管家等民生向功能。

> 核心叙事：**把一对一督学的时间编排能力，免费给到每一位县城自习室里的同学。**

## ✨ 项目亮点

- 🧠 **10 项实证研究做硬骨架** — 检索自测 / 交错练习 / 间隔复习 / 自我关怀…… 每一条排序规则都有可查证的同行评议出处
- 🤖 **AI 做软个性化** — 学情诊断 / 每日复盘 / 编排解释（前端可选本地 LLM 或平台托管代理）
- 💛 **暖心护航（情绪守卫）** — 每日打卡 / 4-7-8 呼吸练习 / 危机关键词转介 12355-12356 / 自我关怀话术
- 📅 **考试节点管家** — 报名 / 确认 / 准考证节点追踪，今日页倒计时 chip 提醒
- 🌍 **目标模板库** — 考研 / 期末 / 考公 / 教资 / 法考 / 软考 / 四六级，8 种预设一键载入
- ♿ **无障碍适配** — 大字模式 / aria-label / focus-visible 键盘焦点环 / Toast 读屏播报
- 💾 **数据主权** — 本地 SQLite 文件随项目打包，参赛「数据归属用户」叙事；老 localStorage 数据可一键迁移到云端
- 📦 **极简部署** — 一个 `npm install && npm start`，无需额外数据库；Docker / 云服务 / 阿里云轻量均可

## 🚀 快速开始

### 1. 跑前端 demo（无后端，纯 localStorage）

直接用浏览器打开 [`index.html`](./index.html) 即可体验全部民生功能。

### 2. 跑全栈版（带账号体系 + 数据云同步）

```bash
cd server
npm install
cp .env.example .env
# 编辑 .env，至少改 JWT_SECRET 为一个长随机串
npm run dev
```

打开 [http://localhost:3000/app](http://localhost:3000/app)，启动页会出现「☁️ 启用云同步」按钮。

### 3. Docker 部署

```bash
cd server
docker build -t zhixu-study .
docker run -d -p 3000:3000 \
  -v $(pwd)/data:/app/data \
  -e JWT_SECRET="$(node -e 'console.log(require(\"crypto\").randomBytes(48).toString(\"base64\"))')" \
  zhixu-study
```

详细部署文档见 [`server/README.md`](./server/README.md)。

## 📂 目录结构

```
zhixu-study/
├── index.html                    # 单文件前端（130 KB，民生功能完整）
├── server/                       # Next.js 14 全栈后端
│   ├── app/                      #   API 路由 + 页面
│   ├── lib/                      #   数据层 / 认证 / 响应助手
│   ├── public/                   #   前端副本 + api-client.js 云适配
│   ├── scripts/                  #   数据迁移工具
│   ├── Dockerfile
│   └── README.md
├── pdf-assets/                   # 参赛方案文档的图表素材
└── 云帆-参赛作品应用方案.pdf     # 参赛作品应用方案文档
```

## 🧬 实证依据（10 条）

| 编号 | 关键效应 | 应用场景 |
|---|---|---|
| 1 | 自我效能循环（Bandura） | 首胜开场 |
| 2 | 进步感（Progress Principle） | 连续打卡视觉化 |
| 3 | 认知负荷（Cognitive Load） | 难题分散 + 短时长块 |
| 4 | 检索自测效应（Roediger & Karpicke） | 时表中插入小测 |
| 5 | 交错练习（Interleaving） | 同类多科目切换 |
| 6 | 间隔复习（Spacing） | 跨日回顾 |
| 7 | 蔡格尼克效应（Zeigarnik） | 悬念收尾任务块 |
| 8 | 自我决定理论（SDT） | 自主感 / 胜任感 / 关系感 |
| 9 | 意志力损耗之争（Ego Depletion） | 不采用先难后易防耗尽 |
| 10 | 自我关怀（Neff, 2003） | 连击中断 / 低情绪关怀 |

每条规则的具体出处和应用方式，见前端「科学依据」页。

## 🛟 民生向功能

云帆不只想做工具，更想做民生服务：

- **教育公平**：核心功能免费，小程序/纯静态版本下到县乡自习室
- **心理守卫**：12355 转介、4-7-8 呼吸练习、自我关怀卡
- **考试节点管家**：错过一个节点 = 全年备考白费，云帆替你盯着
- **数据主权**：你的情绪数据、备考计划，都在你自己的设备/服务器上

## 🧪 技术栈

- **前端**：原生 HTML + CSS + Vanilla JS（单文件可静态托管），无构建工具
- **后端**：Next.js 14 (App Router) + TypeScript + better-sqlite3 + JWT (jose) + bcryptjs
- **数据库**：SQLite（单文件部署友好，可平滑替换 libSQL 云端）
- **部署**：Docker / Node.js / 阿里云轻量 / 腾讯云 Serverless 都可

## 📜 License

MIT — 鼓励非商业场景免费使用，欢迎二次开发与社区贡献。

## 🤝 致谢

感谢 9 项认知科学研究与 1 项动机心理学研究的原作者们——是这些实证证据让
「云帆」的每一个排序决定都有据可查，而不是凭感觉。

---

> 长风破浪会有时，直挂云帆济沧海。🌊