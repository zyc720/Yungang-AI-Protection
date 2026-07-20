# 云冈石窟智能电子辞典 — 系统启动指南

## 架构概览

```
浏览器 (localhost:5173)
    ↓
FastAPI 后端 (localhost:8000)
    ↓
vLLM 模型服务 (localhost:8002)  ← DeepSeek-R1-Distill-Qwen-32B-AWQ
    ↓
Milvus 向量数据库 (嵌入式 Lite 模式)
    ↓
《云冈石窟辞典》知识库 (~2300 词条)
```

## 前置条件

| 组件 | 要求 |
|------|------|
| Python | 3.11+（Conda 环境 `yungang` 用于后端，`vllm_env` 用于模型） |
| Node.js | 18+（前端） |
| GPU | NVIDIA RTX 5090 32GB（vLLM 本地推理） |
| 磁盘 | 模型约 18GB，项目约 500MB |

---

## 一、启动 vLLM 模型服务（终端 1）

```bash
cd /home/haoyue/Projects/Yungang-dictionaryRAG
./scripts/start_vllm.sh
```

等待约 30-60 秒，看到以下输出即启动成功：

```
INFO:     Uvicorn running on http://0.0.0.0:8002
```

**验证**：
```bash
curl http://localhost:8002/v1/models
```

> **切换为 DeepSeek 云端 API**：修改 `backend/.env` 中 `LLM_PROVIDER=deepseek` 并填入 `DEEPSEEK_API_KEY`，可跳过本步骤。

---

## 二、启动 FastAPI 后端（终端 2）

```bash
cd /home/haoyue/Projects/Yungang-dictionaryRAG/backend

# 首次运行需安装依赖
pip install -r requirements.txt

# 启动
python main.py
```

默认监听 `http://0.0.0.0:8000`。

**API 端点**：

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/search` | 纯文档检索（不调用 LLM） |
| `POST` | `/api/chat` | RAG 全链路：检索 → LLM → 答案 + 引用 |
| `GET` | `/api/health` | 健康检查（含 Milvus 状态） |

**验证**：
```bash
curl http://localhost:8000/api/health
```

---

## 三、启动前端（终端 3）

```bash
cd /home/haoyue/Projects/Yungang-dictionaryRAG/frontend

# 首次运行需安装依赖
npm install

# 启动开发服务器
npm run dev
```

默认监听 `http://localhost:5173`，API 请求自动代理到后端 `:8000`。

---

## 四、知识库初始化（首次运行）

如果尚未导入知识库数据：

```bash
cd /home/haoyue/Projects/Yungang-dictionaryRAG/backend

# 仅打印统计信息，不写入数据库
python scripts/ingest_knowledge.py --stats-only

# 正式导入到 Milvus（需要 BGE-M3 模型，首次下载约 2GB）
python scripts/ingest_knowledge.py
```

> 导入后，`chunks.json` 和 `chunks_milvus.json` 会保存在 `backend/data/`。

---

## 五、功能验证

### 1. 健康检查

```bash
curl -s http://localhost:8000/api/health | python -m json.tool
```

### 2. 文档检索

```bash
curl -s -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "云冈石窟", "top_k": 3}' | python -m json.tool
```

### 3. RAG 问答

```bash
curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "云冈石窟建于何时？", "top_k": 5}' | python -m json.tool
```

### 4. 前端界面

浏览器打开 `http://localhost:5173`，在搜索框输入问题即可。

---

## 六、停止服务

按对应终端的 `Ctrl+C` 依次停止：

1. 前端（Vite dev server）
2. 后端（FastAPI）
3. vLLM 模型服务

---

## 七、配置文件速查

### `backend/.env`（核心配置）

```ini
# LLM 后端选择：vllm（本地）或 deepseek（云端）
LLM_PROVIDER=vllm

# vLLM 本地部署
VLLM_BASE_URL=http://localhost:8002/v1
VLLM_MODEL=casperhansen/deepseek-r1-distill-qwen-32b-awq

# DeepSeek 云端 API（LLM_PROVIDER=deepseek 时生效）
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat

# Milvus（开发模式使用嵌入式 Lite）
USE_MILVUS_LITE=true
MILVUS_COLLECTION_NAME=knowledge_chunks

# BGE-M3 嵌入模型
BGE_MODEL_NAME=BAAI/bge-m3
EMBEDDING_DEVICE=cpu

# 检索
RETRIEVAL_TOP_K=5
```

### `scripts/start_vllm.sh`（vLLM 启动参数）

```bash
# 可通过环境变量覆盖
VLLM_PORT=8002
VLLM_GPU_MEM_UTIL=0.90
VLLM_MAX_MODEL_LEN=8192
```

---

## 八、常见问题

| 问题 | 解决方法 |
|------|----------|
| `Connection refused :8002` | vLLM 未启动或模型仍在加载中 |
| `Collection not found` | 运行 `python scripts/ingest_knowledge.py` 导入数据 |
| 显存不足 (OOM) | 调低 `VLLM_GPU_MEM_UTIL=0.75` 或 `VLLM_MAX_MODEL_LEN=4096` |
| BGE-M3 下载慢 | 模型首次加载会自动下载到 `~/.cache/huggingface/`，约 2GB |
| 前端页面空白 | 检查后端 `:8000` 是否正常运行 |
