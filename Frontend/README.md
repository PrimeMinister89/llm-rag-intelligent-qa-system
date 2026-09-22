# Frontend — LLM-RAG Intelligent QA System

> 基于 Vue 3 + TypeScript + Element Plus 的智能问答前端，提供多轮对话、文件上传、历史会话回看与 Agent 开关等交互能力。

## 📖 简介

前端是一个单页应用（SPA），核心界面集中在 [src/App.vue](./src/App.vue)。左侧为历史侧边栏（问题记录 / 文件信息两个 Tab），右侧为主聊天区，包含回复展示、问题输入框、Agent 开关以及 Search / Upload / Clean 三个操作按钮。用户输入问题后通过 Axios 以 `FormData` 形式 POST 到后端 `/chat` 接口，并接收 AI 回复渲染到界面。

## ✨ 功能特性

- 💬 **多轮问答**：输入框 + 回复区，支持连续提问。
- 🧠 **Agent 开关**：`el-switch` 启用后，后端将走 Agent 联网搜索链路。
- 📤 **文件上传**：弹窗内拖拽 / 点击上传，支持多文件待传缓冲区，提交时随问题一起发送给后端做 RAG。
- 🧹 **文件清理**：一键清空待传文件缓冲区与文件历史。
- 🗂️ **历史会话**：左侧“问题记录” Tab 列出历史问题，点击即可回看对应回复；“开启新对话”按钮调用后端 `/reset` 清空记忆。
- ⏳ **加载态**：请求期间主区域显示 `v-loading` 蒙层。
- 🍞 **消息提示**：使用 Element Plus `ElMessage` 反馈上传 / 清理 / 新对话等操作结果。

## 🧰 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue 3（Composition API + `<script setup>`） | ^3.5 |
| 语言 | TypeScript | ~5.8 |
| 构建 | Vite | ^7.0 |
| UI | Element Plus | ^2.10 |
| 状态 | Pinia | ^3.0 |
| 路由 | Vue Router | ^4.5 |
| 请求 | Axios | ^1.10 |
| 开发工具 | vite-plugin-vue-devtools | ^7.7 |

## 📁 目录结构

```
Frontend/
├── public/                     # 静态资源
├── src/
│   ├── App.vue                 # 聊天主界面（侧边栏 + 输入 + 回复 + 上传弹窗）
│   ├── main.ts                 # 应用入口（注册 Pinia / Router / ElementPlus）
│   ├── router/index.ts         # 路由配置（/ 与 /about）
│   ├── stores/counter.ts       # Pinia 示例 store
│   ├── views/                  # 页面（HomeView / AboutView）
│   ├── components/             # 通用组件与图标
│   └── assets/                 # 全局样式
├── index.html
├── vite.config.ts              # Vite 配置（含 @ → ./src 别名）
├── tsconfig*.json              # TypeScript 配置
├── env.d.ts                    # Vue SFC 类型声明
└── package.json
```

## 🛠️ 环境与 IDE

- 推荐使用 [VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar)（请禁用旧版 Vetur）。
- TypeScript 默认无法处理 `.vue` 类型，项目使用 `vue-tsc` 替代 `tsc` 进行类型检查。

## 🚀 安装与运行

```sh
# 安装依赖
npm install

# 开发模式（热更新）
npm run dev

# 类型检查 + 生产构建
npm run build

# 预览生产构建产物
npm run preview

# 仅类型检查
npm run type-check
```

开发模式下，Vite 默认监听 http://localhost:5173。

## 🔌 与后端联调

前端在 [src/App.vue](./src/App.vue) 中硬编码了后端地址：

- `POST http://localhost:8000/chat`：发送问题 / 文件 / Agent 开关。
- `POST http://localhost:8000/reset`：开启新对话时清空后端记忆。

请确保后端已启动并监听 8000 端口；如需修改地址，请在上述文件中同步替换。后端已开启 CORS（`allow_origins=["*"]`），本地开发无需额外代理配置。

## 📨 请求字段说明

`/chat` 请求体为 `FormData`：

| 字段 | 说明 |
|------|------|
| `message` | 用户输入的问题文本 |
| `value1` | Agent 开关状态，`"true"` / `"false"` 字符串 |
| `files` | 可选，多文件数组，随问题一起上传做 RAG |

## ⚙️ 自定义配置

Vite 配置详见 [vite.config.ts](./vite.config.ts)，已设置 `@` 别名指向 `./src`。更多 Vite 配置参考 [官方文档](https://vite.dev/config/)。
