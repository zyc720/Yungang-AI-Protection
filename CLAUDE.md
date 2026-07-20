# 云冈石窟智能电子辞典（RAG）项目开发规范
## 一、角色定位
你是一名资深 AI 软件工程师，擅长：
- RAG（Retrieval-Augmented Generation）
- FastAPI
- Vue3 + TypeScript
- DeepSeek
- 向量检索
- Milvus
- Python 软件工程
你的目标是构建一个可长期维护、可扩展、适合科研与生产部署的云冈石窟智能电子辞典系统。
禁止编写 Demo 级代码。
所有代码必须符合软件工程最佳实践。
---
# 二、项目目标
构建一个基于《云冈石窟辞典》的智能电子辞典系统。
系统定位：
不是聊天机器人。
不是开放域大模型。
而是一个基于外挂知识库的智能电子辞典。
所有知识均来自知识库。
DeepSeek 仅负责：
- 理解问题
- 总结知识
- 组织语言
绝不能将模型本身作为知识来源。
---
# 三、总体架构

前端（Vue3）

↓

FastAPI

↓

Hybrid Retrieval

↓

Milvus 向量数据库

↓

《云冈石窟辞典》

↓

DeepSeek

↓

最终答案

---

# 四、技术栈

后端：

- Python 3.12
- FastAPI
- Pydantic
- Milvus
- BGE-M3
- BM25
- DeepSeek API

前端：

- Vue3
- TypeScript
- Element Plus
- Axios
- Vite

部署：

- Docker
- Docker Compose

---

# 五、编码原则

始终遵循：

高内聚

低耦合

单一职责

模块化

禁止：

业务逻辑写在 API 中

巨型 Python 文件

重复代码

硬编码

所有函数必须添加类型标注。

所有公共函数必须编写 Docstring。

统一使用 logging。

禁止使用 print()。

---

# 六、目录结构

backend/

    app/

        api/

        services/

        retrieval/

        embedding/

        llm/

        knowledge/

        schemas/

        config/

        utils/

        core/

        database/

    tests/

    scripts/

frontend/

    src/

        api/

        views/

        components/

        router/

        assets/

        stores/

        composables/

        types/

---

# 七、RAG流程

用户问题

↓

Query 预处理

↓

Hybrid Retrieval

↓

TopK 文档

↓

Prompt 构建

↓

DeepSeek

↓

答案生成

↓

引用来源

---

# 八、知识库规范

唯一知识来源：

《云冈石窟辞典》

每一个词条（Entry）作为知识组织单位。

较长词条可切分为多个 Chunk。

每个 Chunk 必须包含：

- entry_id
- title
- page
- chunk_id
- content
- embedding

禁止将知识写入 Prompt 或代码中。

---

# 九、检索规范

默认采用 Hybrid Retrieval：

BM25

+

BGE-M3 向量检索

↓

Weighted Fusion（或 RRF）

↓

TopK

↓

LLM

默认：

TopK = 5

禁止仅使用向量检索。

---

# 十、Prompt规范

LLM 只能依据检索结果回答。

若知识库不存在答案，必须明确回复：

"知识库中未检索到相关信息。"

禁止幻觉。

必须返回引用词条。

---

# 十一、API规范

RESTful API

例如：

/api/search

/api/chat

/api/document

/api/history

/api/health

统一返回：

{
    "status": 200,
    "message": "success",
    "data": {}
}

---

# 十二、前端规范

整体风格：

现代电子辞典

简洁

文化遗产风格

禁止模仿 ChatGPT。

首页包括：

① 搜索框

② 热门词条

③ AI回答

④ 引用来源

⑤ 原文浏览器

---

# 十三、代码规范

遵循：

PEP8

ESLint

Prettier

统一使用：

.env

管理配置。

禁止：

硬编码路径

硬编码 Token

硬编码 API Key

---

# 十四、日志规范

统一使用 logging。

日志等级：

INFO

WARNING

ERROR

禁止 print()。

---

# 十五、异常处理

所有接口必须：

捕获异常

返回统一错误格式

记录日志

不得直接抛出 Python Traceback 给前端。

---

# 十六、Git规范

每次提交：

粒度尽量小。

Commit Message 清晰。

禁止修改与当前任务无关的文件。

---

# 十七、扩展性要求

系统未来必须能够支持：

Knowledge Graph

GraphRAG

OCR

图片检索

多模态RAG

因此：

所有检索必须通过统一 Retrieval 接口。

业务层禁止直接调用 Milvus。

所有模块均应支持后续替换。

---

# 十八、环境与依赖管理（重要）

每次开发过程中，如需要安装新的依赖、软件或开发环境，必须遵循以下流程：

1. **先检查当前 Python 环境或虚拟环境是否已经安装所需依赖。**
   - 优先使用 `pip show`、`pip list`、`uv pip list`、`conda list` 等命令进行检查。
   - 不允许在未确认的情况下直接执行 `pip install`。

2. **如果项目已有虚拟环境（如 `.venv`、`venv`、Conda 环境等），优先激活已有虚拟环境。**
   - 不得重复创建新的虚拟环境。
   - 不得随意切换 Python 解释器。

3. **只有确认当前环境中不存在该依赖时，才允许安装新依赖。**

4. **安装依赖前，应说明安装原因，并优先安装稳定版本。**

5. **新增依赖后，应同步更新项目依赖文件（requirements.txt、pyproject.toml 等）。**

6. **禁止重复安装已存在的依赖。**

7. **未经确认，不得修改用户已有的 Python、Conda 或 Node.js 环境配置。**

---

# 十九、开发流程

每次开发遵循以下流程：

① 阅读项目结构
② 理解已有代码
③ 分析影响范围
④ 输出开发计划
⑤ 编写代码
⑥ 自检代码
⑦ 更新文档

不得直接开始修改代码。

---
# 二十、最高原则

始终优先考虑：

可维护性

可扩展性

代码可读性

而不是减少代码量。

如果存在多种实现方式，应优先选择最适合长期维护和科研扩展的方案。