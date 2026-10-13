# 云帆 · AI 学习领航引擎 — 后端服务

> **让每一次自习室里的埋头，都被科学看见。**

这是参赛作品「云帆」的全栈版本。前端是 `index.html`（保留原版民生功能：暖心护航、考试节点管家、目标模板库、无障碍适配），后端新增 Next.js 14 + JWT + SQLite，提供：

- 完整账号体系（注册/登录/JWT/httpOnly cookie）
- 学科档案、每日计划、完成记录、情绪数据、考试节点等资源的云同步
- 多设备续连击（旧 localStorage 数据可一键迁移）
- 民生数据由用户主权（SQLite 文件随项目一起打包）

## 目录速览

```
server/
├── app/
│   ├── api/             # REST API 路由
│   │   ├── auth/        # 注册、登录、注销、当前用户
│   │   ├── subjects/    # 学科档案
│   │   ├── plans/       # 每日任务计划
│   │   ├── completions/ # 完成记录
│   │   ├── moods/       # 情绪打卡
│   │   ├── nodes/       # 考试节点
│   │   ├── profile/     # 用户偏好
│   │   ├── ai/          # AI 教练代理（占位实现）
│   │   └── health/      # 健康检查
│   ├── layout.tsx
│   └── page.tsx         # 重定向到 /app
├── lib/                 # 通用工具
│   ├── db.ts            # SQLite 数据层（含自动建表迁移）
│   ├── auth.ts          # JWT / bcrypt / cookie
│   └── api.ts           # 统一响应 / 错误处理 / 限流
├── public/
│   └── index.html       # 单文件前端（民生版本）
├── scripts/
│   ├── init.ts          # 手动初始化数据库
│   └── migrate.ts       # 从 localStorage 导入
├── data/                # SQLite 文件目录（运行时生成，git 忽略）
├── package.json
├── tsconfig.json
├── next.config.mjs
├── .env.example
├── Dockerfile
└── README.md            # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
cd server
npm install
```

> Windows 用户如遇到 `better-sqlite3` 编译失败，请先安装 [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) 或使用 `npm config set msvs_version 2022`。Linux/macOS 用户确保安装了 Python 3 + make。

### 3. 配置环境变量

```bash
cp .env.example .env
```

修改 `JWT_SECRET` 为至少 32 位随机字符串：

```bash
node -e "console.log(require('crypto').randomBytes(48).toString('base64'))"
```

### 4. 启动开发服务器

```bash
npm run dev
```

打开 [http://localhost:3000](http://localhost:3000) 即可访问。

### 5. 初始化数据库（可选）

首次启动时会自动建表。如需手动初始化：

```bash
npm run db:init
```

## 生产部署

### 方案 A：本地 Node 直接部署（最简单）

```bash
npm run build
npm start
```

把 `server/data/zhixu.db` 备份即可保证数据不丢。

### 方案 B：Docker 部署（推荐）

```bash
docker build -t zhixu-study .
docker run -d \
  --name zhixu-study \
  -p 3000:3000 \
  -v $(pwd)/data:/app/data \
  -e JWT_SECRET="$(node -e 'console.log(require(\"crypto\").randomBytes(48).toString(\"base64\"))')" \
  zhixu-study
```

数据库通过 `-v` 挂载到宿主机的 `./data/`，容器重启数据不丢。

### 方案 C：部署到云

- **阿里云轻量应用 Server / 腾讯云轻量 Server**：直接装 Node.js 20+，按方案 A 操作。
- **Railway / Render**：连接 GitHub 仓库，自动构建；环境变量填入 `JWT_SECRET` 即可。
- **Vercel**：Next.js 天然支持；但 SQLite 需要换成 Turso（libSQL 云数据库），改造点见下方。

### 替换为云数据库

`lib/db.ts` 是唯一与 SQLite 耦合的地方。参赛作品如需上 Vercel：

1. 安装 `@libsql/client` 替代 `better-sqlite3`
2. 把 `lib/db.ts` 里的 `Database` 类替换为 `createClient` 接口
3. 所有 `prepare / run / get / all` 调用改为对应的 client 方法即可

迁移指南：<https://docs.turso.tech/libsql/client-accessors>

## 数据迁移（localStorage → SQLite）

给老用户保留原有数据：

1. 在前端添加「导出数据」按钮（生成 `import.json`）
2. 用户把该文件放到 `server/data/import.json`
3. 执行：

```bash
npm run db:migrate -- user@example.com
```

脚本会创建账号（临时密码打印在终端）并导入全部数据。

## API 速览

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/auth/register` | 注册 |
| `POST` | `/api/auth/login` | 登录 |
| `POST` | `/api/auth/logout` | 注销 |
| `GET` | `/api/auth/me` | 当前用户 |
| `GET` | `/api/subjects` | 学科列表 |
| `POST` | `/api/subjects` | 批量保存（覆盖语义） |
| `GET` | `/api/plans?date=YYYY-MM-DD` | 拉某日计划 |
| `POST` | `/api/plans` | 写入某日计划 |
| `GET` | `/api/completions?from=&to=` | 完成记录 |
| `POST` | `/api/completions` | 标记完成 |
| `DELETE` | `/api/completions?date=` | 取消当日所有完成 |
| `GET` | `/api/moods?from=&to=` | 情绪记录 |
| `POST` | `/api/moods` | 打卡 |
| `GET` | `/api/nodes?from=&to=` | 考试节点 |
| `POST` | `/api/nodes` | 新增节点 |
| `PATCH` | `/api/nodes?id=` | 标记完成 / 取消 |
| `DELETE` | `/api/nodes?id=` | 删除节点 |
| `GET` | `/api/profile/preferences` | 用户偏好 |
| `POST` | `/api/profile/preferences` | 保存偏好 |
| `POST` | `/api/ai` | AI 教练代理（需配置） |
| `GET` | `/api/health` | 健康检查 |

所有接口（`auth/*` 和 `health` 除外）都需要登录，401 表示未登录或 token 过期。

## 安全设计

- 密码 bcrypt（10 轮），从不明文存储
- JWT 走 httpOnly + SameSite=Lax cookie，XSS 风险最小化
- 路由级 `requireSession()` 守卫，确保只访问自己的数据
- 所有 SQL 走预编译参数，杜绝注入
- 每分钟 60 次/AI 路由 20 次的限流

## 民生叙事

云帆做的不只是一个学习工具：

1. **教育公平**：核心功能免费，小程序/纯静态版本下到县乡自习室
2. **心理守卫**：12355 转介、4-7-8 呼吸练习、自我关怀卡
3. **考试节点管家**：错过一个节点 = 全年备考白费，云帆替你盯着
4. **数据主权**：你的情绪数据、备考计划，都在你自己的设备/服务器上

参评论文 / 答辩时可用：

> **「云帆不只想做工具，更想做民生服务。把督学的时间编排能力，免费给到每一位自习室里的同学。」**

## License

MIT — 鼓励非商业场景免费使用