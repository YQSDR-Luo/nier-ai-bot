
# 🤖 尼尔AI万事通 (NieR: Automata AI Expert)

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.47-ff4b4b.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**一个基于检索增强生成（RAG）技术的《尼尔：机械纪元》主题AI问答机器人。它不仅能准确回答关于游戏世界观、剧情和角色的问题，还能展示其背后的思考过程，并提供优雅、实时的交互体验。**

---

### 🌟 项目演示 (Project Demo)

![项目动态演示GIF](https://github.com/user-attachments/assets/f07ed3d0-4760-434b-9a4e-02ca40002ffe)

### ✨ 主要特性 (Key Features)

*   **先进的RAG架构:** 整个应用基于现代大语言模型应用中最核心的检索增强生成（RAG）技术，确保回答的准确性和时效性。
*   **定制化知识库:** 从零开始，手工构建了一个关于《尼尔：机械纪元》的、包含超过60个主题、240+知识块的结构化知识库。
*   **流式响应与打字机效果:** AI的回答以流式（Streaming）方式实时生成，并以优雅的打字机效果呈现，提供了极致的交互体验。
*   **思考过程可视化:** 创新的UI设计，能够实时展示AI在回答前的“思考（Reasoning）”过程，让黑盒模型变得透明。
*   **动态实时UI反馈:** 界面在检索、思考、回答的每一步都有明确、非阻塞的即时反馈，解决了用户等待时的未知焦虑。
*   **优雅的iOS设计美学:** 借鉴iOS设计哲学，通过自定义CSS实现了简洁、美观的UI界面，包括动态的消息进入动画。
*   **企业级开发实践:**
    *   **环境变量管理:** 将API Key等敏感信息存储在环境变量中，保障代码安全。
    *   **环境依赖管理:** 使用Conda的`environment.yml`文件精确管理项目环境，保证了项目的可复现性。
    *   **代码重构:** 将核心逻辑封装成函数和独立模块，提高了代码的可读性和可维护性。

### 🛠️ 技术栈 (Technology Stack)

| 技术分类 | 主要技术 |
| :--- | :--- |
| **后端/核心逻辑** | Python 3.12 |
| **Web UI框架** | Streamlit |
| **环境管理** | Conda |
| **向量嵌入模型** | BAAI/bge-m3 (通过Silicon Flow API调用) |
| **语言生成模型** | Qwen3 (通过Silicon Flow API调用) |
| **向量数据库** | ChromaDB (本地持久化存储) |
| **API交互** | OpenAI Python SDK, Requests |

### 🏗️ 项目架构 (Architecture)

本项目的核心是一个完整的RAG（检索增强生成）流程：

1.  **知识库构建 (离线):** 手动收集和整理《尼尔：机械纪元》的资料，切分成独立的知识块。
2.  **数据持久化 (离线):** 运行 `main.py` 脚本，将所有知识块通过Embedding API向量化，并存入本地的ChromaDB向量数据库。
3.  **用户交互 (在线):**
    *   用户在Streamlit前端界面输入问题。
    *   **检索(Retrieve):** 应用将用户问题向量化，并在ChromaDB中检索出最相关的知识片段。
    *   **增强(Augment):** 将原始问题和检索到的知识片段，共同组合成一个内容丰富的Prompt。
    *   **生成(Generate):** 将增强后的Prompt发送给大语言模型（LLM），LLM会参考提供的知识，生成思考过程和最终答案。
    *   **流式呈现:** 生成的内容以流式方式返回前端，并以动态效果实时展示给用户。

### 🚀 快速开始 (Getting Started)

请按照以下步骤在本地运行本项目。

#### 1. 先决条件

*   确保你已经安装了 [Git](https://git-scm.com/)。
*   确保你已经安装了 **Miniconda** 或 **Anaconda**。

#### 2. 克隆项目

```bash
git clone [你的GitHub仓库链接]
cd nier-ai-bot
```

#### 3. 创建并激活Conda环境

本项目使用`environment.yml`文件来确保环境的一致性。请确保该文件在你的项目根目录中。

```bash
# 使用environment.yml文件创建名为"nier"的Conda环境
# 这个命令会自动安装所有指定的conda和pip依赖包
conda env create -f environment.yml

# 激活新创建的环境
conda activate nier
```

#### 4. 设置环境变量

本项目需要一个API Key来调用模型服务。请在你的操作系统中设置一个名为 `SILICONFLOW_API_KEY` 的环境变量。

*   **Windows:** 按照本项目之前的教程进行设置。
*   **macOS / Linux:** 在你的 `.zshrc` 或 `.bashrc` 文件中添加 `export SILICONFLOW_API_KEY="你的sk-xxxx密钥"`，然后运行 `source ~/.zshrc`。

**重要提示:** 设置完环境变量后，请**重启你的终端**以确保其生效。

#### 5. 初始化知识库

在第一次运行Web应用前，你需要先填充向量数据库。请确保你已在`nier`环境中。

```bash
python main.py
```
*(请注意，此过程会调用API并消耗额度，总共约240+次调用)*

#### 6. 启动Web应用

```bash
streamlit run app.py
```

应用将在你的浏览器中自动打开！

### 🤝 贡献指南 (Contributing)

欢迎各种形式的贡献！如果你有任何想法或建议，请随时提交一个Issue或Pull Request。

### 📄 许可证 (License)

本项目采用 [MIT License](LICENSE) 授权。

