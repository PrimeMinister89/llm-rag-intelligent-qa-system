
# Backend — LLM-RAG Intelligent QA System

> 基于 FastAPI + LangChain 的智能问答后端，提供多轮对话、文件 RAG、图片 VQA 与 Agent 联网搜索能力。

## 📖 简介

后端核心实现集中在 [backend.py](./backend.py) 中。它对外暴露两个 HTTP 接口，内部根据请求参数自动路由到四种处理链路：

1. **普通 LLM 对话**：直接调用 GLM-4，结合 `ConversationBufferMemory` 维持多轮上下文。

2. **Agent 联网搜索**：启用 `CONVERSATIONAL_REACT_DESCRIPTION` Agent，结合 SerpApi 工具获取实时信息后回答。

3. **文件 RAG**：解析用户上传的 `.txt` / `.docx` / `.pdf`，分块后写入 Chroma 向量库，检索 Top-6 片段拼接到 RAG Prompt 中生成回复。

4. **图片 VQA**：对 `.jpg` 图片使用 Salesforce BLIP（`blip-vqa-base`）模型进行视觉问答。

## 🧰 技术栈

- **Web 框架**：FastAPI + Uvicorn

- **LLM 编排**：LangChain（langchain / langchain-openai / langchain-community / langchain-chroma / langchain-text-splitters / langchain-huggingface）

- **大模型**：GLM-4（智谱 AI，OpenAI 兼容接口 `https://open.bigmodel.cn/api/paas/v4` ）

- **Embedding**：Jina Embeddings v4

- **向量库**：Chroma（本地内存持久化）

- **多模态**：Salesforce BLIP VQA（HuggingFace Transformers + PyTorch + Pillow）

- **文档解析**：PyMuPDF（PDF）、python-docx（Word）

- **联网工具**：SerpApi（通过 `langchain_community.agent_toolkits.load_tools` 加载）

- **配置**：python-dotenv

- **跨域**：FastAPI CORSMiddleware（允许所有来源）

## 🔑 环境变量

在 `Backend/` 目录下创建 `.env` 文件：

```env
ZHIPU_API_KEY=your_zhipu_api_key        # 必填，GLM-4 模型密钥
JINA_API_KEY=your_jina_api_key          # 必填，文本 Embedding 密钥
SERPAPI_API_KEY=your_serpapi_key        # 启用 Agent 时必填

```

代码中通过 `load_dotenv()` + `os.getenv(...)` 读取。

## 🛠️ 安装与运行

```bash
cd Backend

# 1. 创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\activate            # Windows

# source .venv/bin/activate      # macOS / Linux

# 2. 安装依赖
pip install fastapi uvicorn python-dotenv \
            langchain langchain-openai langchain-community \
            langchain-chroma langchain-text-splitters langchain-huggingface \
            chromadb python-docx pymupdf transformers torch pillow numpy \
            google-search-results

# 3. 配置 .env（参考上一节）

# 4. 启动服务（默认监听 8000 端口，前端硬编码访问 http://localhost:8000 ）
uvicorn backend:app --reload --port 8000

```

启动后访问 http://localhost:8000/docs 可查看 FastAPI 自动生成的交互式 API 文档。

> 注：运行过程中会在工作目录临时生成 `temp.docx` / `temp.pdf` 用于文档解析。

## 📡 接口文档

### POST `/chat`

主问答接口。请求体为 `multipart/form-data`。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message` | string (Form) | ✅ | 用户输入的问题 |
| `value1` | string (Form) | ✅ | 是否启用 Agent 模式，传字符串 `"true"` 表示启用，其它表示否 |
| `files` | list[UploadFile] (Form) | ❌ | 上传的文件列表，支持 `.txt` / `.docx` / `.pdf` / `.jpg` |

**响应**：`{ "reply": "AI 生成的回复文本" }`

**处理分支（按优先级）**：

1. `value1 == "true"` → 走 Agent 链路，使用 SerpApi 联网搜索后回答。

2. `len(files) > 0` → 走文件处理链路：
   - `.txt`：直接读取 UTF-8 文本。
   - `.docx`：写入临时文件后用 `python-docx` 提取段落文本。
   - `.pdf`：写入临时文件后用 `PyMuPDFLoader` 提取页面文本。
   - `.jpg`：使用 BLIP VQA 模型直接对图片 + 问题生成答案并返回。
   - 文本类文件统一经过 `RecursiveCharacterTextSplitter`（chunk=500, overlap=50）切分，写入 Chroma，检索 Top-6 片段，组装 RAG Prompt 后调用 GLM-4 生成回复。

3. 其它情况 → 走普通 LLM 对话链路，结合 `ConversationBufferMemory` 维持上下文。

### POST `/reset`

清空对话记忆，开启新会话。

**请求体**：`{ "new_session": true }`

**响应**：无具体返回体（成功即为 200）。

## 🔧 关键实现说明

- **Prompt 模板**：系统 Prompt 设定为“以幽默语气与人类对话的 AI 助手”，包含 `chat_history` 与 `human_input` 两个变量。

- **Memory**：使用 `ConversationBufferMemory`，在普通对话分支中手动 `save_context` 写入上下文。

- **Agent**：`initialize_agent` 使用 `CONVERSATIONAL_REACT_DESCRIPTION` 类型，`max_iterations=3`，`handle_parsing_errors=True`，自动加载 `serpapi` 工具。

- **RAG 链路**：`retriever | format_docs` 作为 `context`，`RunnablePassthrough()` 作为 `question`，再经 `rlm/rag-prompt`（从 LangChain Hub 拉取）→ GLM-4 → `StrOutputParser`，使用 `.stream()` 流式拼装结果。

- **CORS**：开启 `allow_origins=["*"]`，便于前端本地开发联调。

## ⚠️ 注意事项

- 前端硬编码请求 `http://localhost:8000` ，如需修改端口请同步调整 [Frontend/src/App.vue](../Frontend/src/App.vue) 中的请求地址。

- BLIP 模型首次运行会从 HuggingFace 下载权重，需保证网络畅通。

- `temp.docx` / `temp.pdf` 为运行时临时文件，可安全删除。

- 生产环境请收紧 CORS 策略并妥善保管 API Key，切勿提交 `.env`。

