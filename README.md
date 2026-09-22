# LLM-RAG Intelligent QA System

> 基于 GLM-4 大模型与检索增强生成（RAG）的智能问答系统，支持多模态文件理解、Agent 联网搜索与多轮对话记忆。

## 📖 项目简介

本项目是一个端到端的智能问答应用，融合了大语言模型（LLM）、检索增强生成（RAG）与多模态视觉问答（VQA）能力。用户可以通过 Web 界面与 AI 进行多轮对话，上传文本 / Word / PDF 文件进行基于知识库的问答，或上传图片进行视觉问答；同时可启用 Agent 模式，让大模型借助 SerpApi 联网搜索获取实时信息后再生成回复。

## ✨ 核心特性

- 🧠 **多轮对话记忆**：基于 `ConversationBufferMemory`，保留上下文实现连续问答。

- 📄 **文档 RAG 问答**：支持 `.txt` / `.docx` / `.pdf` 文件，自动分块、向量化并检索生成。

- 🖼️ **图片视觉问答（VQA）**：基于 Salesforce BLIP 模型对 `.jpg` 图片进行问答。

- 🌐 **Agent 联网搜索**：可启用 `CONVERSATIONAL_REACT_DESCRIPTION` Agent，借助 SerpApi 获取实时信息。

- 🎨 **现代化前端**：Vue 3 + TypeScript + Element Plus，提供文件拖拽上传、历史会话回看等交互。

- ⚡ **流式 / 快速响应**：后端使用 FastAPI，异步处理请求；RAG 链路使用 `stream` 输出。

## 🧰 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + TypeScript | Composition API + `<script setup>` |
| 前端构建 | Vite 7 | 极速热更新 |
| 前端 UI | Element Plus 2 | 组件库 |
| 前端状态 | Pinia 3 | 状态管理 |
| 前端路由 | Vue Router 4 | SPA 路由 |
| 前端请求 | Axios | HTTP 客户端 |
| 后端 | FastAPI | 高性能异步 Web 框架 |
| LLM 编排 | LangChain | 链 / Agent / Memory / RAG |
| 大模型 | GLM-4 | 智谱 AI（OpenAI 兼容接口） |
| 向量库 | Chroma | 本地向量检索 |
| Embedding | Jina Embeddings v4 | 文本向量化 |
| 多模态 | Salesforce BLIP | 图片视觉问答 |
| 文档解析 | PyMuPDF / python-docx | PDF / Word 文本抽取 |
| 联网工具 | SerpApi | 搜索引擎 API |

详细说明请参见各子目录的 README：

- 后端：[Backend/README.md](./Backend/README.md)

- 前端：[Frontend/README.md](./Frontend/README.md)

## 🚀 快速开始

### 前置准备

1. 安装 **Node.js ≥ 18** 与 **npm**。

2. 安装 **Python ≥ 3.10**。

3. 申请以下 API Key：
   - 智谱 AI（GLM-4）：https://open.bigmodel.cn/
   - Jina Embeddings：https://jina.ai/
   - SerpApi（启用 Agent 时需要）：https://serpapi.com/

### 后端启动

```bash
cd Backend
python -m venv .venv
.venv\Scripts\activate            # Windows

# source .venv/bin/activate      # macOS / Linux
pip install fastapi uvicorn python-dotenv langchain langchain-openai langchain-community \
            langchain-chroma langchain-text-splitters langchain-huggingface \
            chromadb python-docx pymupdf transformers torch pillow numpy \
            google-search-results

# 配置 .env（参考 Backend/README.md）
uvicorn backend:app --reload --port 8000

```

### 前端启动

```bash
cd Frontend
npm install
npm run dev

```

浏览器访问 Vite 输出的本地地址（默认 http://localhost:5173 ）即可使用。

## 🔑 环境变量

在 `Backend/.env` 中配置（.env需新建）：

```env
ZHIPU_API_KEY=your_zhipu_api_key
JINA_API_KEY=your_jina_api_key
SERPAPI_API_KEY=your_serpapi_key   # 仅启用 Agent 时必填
```

## 📡 接口概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/chat` | 主问答接口，根据参数自动切换：普通对话 / Agent 联网 / 文件 RAG / 图片 VQA |
| POST | `/reset` | 清空对话记忆，开启新会话 |

详细参数与响应见 [Backend/README.md](./Backend/README.md)。

## 📄 License

本项目仅用于学习与交流。
