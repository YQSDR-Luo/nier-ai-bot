import os
import streamlit as st
import chromadb
from openai import OpenAI
import requests

# --- 准备工作 (保持不变) ---
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY")

def load_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# (后端核心函数部分与之前完全相同，为节省篇幅省略)
@st.cache_resource
def initialize_database():
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, "nier_vector_db")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="nier_automata_kb")
    return collection

@st.cache_data
def get_embedding(text_chunk):
    url = "https://api.siliconflow.cn/v1/embeddings"
    model_name = "BAAI/bge-m3"
    headers = { "Authorization": f"Bearer {SILICONFLOW_API_KEY}", "Content-Type": "application/json" }
    payload = { "model": model_name, "input": text_chunk }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['data'][0]['embedding']
    except Exception:
        return None
    return None

@st.cache_resource
def get_llm_client():
    return OpenAI(api_key=SILICONFLOW_API_KEY, base_url="https://api.siliconflow.cn/v1")

def generate_answer_stream(query, retrieved_chunks, llm_client):
    context = "\n\n---\n\n".join(retrieved_chunks)
    prompt = f"""
请你扮演一个《尼尔：机械纪元》的资深专家。
你的任务是根据下面提供的上下文信息，简洁、清晰地回答用户的问题。
【上下文信息】:
{context}
【用户的问题】:
{query}
"""
    model_name = "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B" 
    stream = llm_client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    return stream


# --- ✨✨✨ 最终完美版 UI ✨✨✨ ---

st.set_page_config(page_title="尼尔AI万事通", page_icon="🤖", layout="centered")
load_css("style.css")

if not SILICONFLOW_API_KEY:
    st.error("错误：未能在系统环境变量中找到 'SILICONFLOW_API_KEY'。")
    st.stop()

collection = initialize_database()
llm_client = get_llm_client()

st.title("尼尔AI万事通")
st.caption("一个基于RAG技术的《尼尔：机械纪元》问答机器人")

# --- 初始化与历史记录显示 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# ✨ 全新、统一的渲染逻辑 ✨
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # 检查是否是结构化的AI回答
        if message["role"] == "assistant" and "final_answer" in message:
            # 渲染检索片段
            if message.get("retrieved"):
                with st.expander("🔍 查看检索到的知识片段", expanded=False):
                    for i, metadata in enumerate(message["retrieved"]["metadatas"]):
                        st.write(f"**片段 {i+1} (来源: {metadata['source']})**")
                        st.caption(message["retrieved"]["documents"][i])
            
            # 渲染思考过程
            if message.get("reasoning"):
                with st.expander("🤔 查看AI的思考过程", expanded=False):
                    st.markdown(message["reasoning"])

            # 渲染最终答案，并在前面加一条分割线
            st.markdown("---")
            st.markdown(message["final_answer"])
        else:
            # 渲染简单的用户消息
            st.markdown(message["content"])


# --- 获取用户输入并开始新的交互流程 ---
if user_prompt := st.chat_input("关于《尼尔：机械纪元》，你有什么想问的？"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        # 步骤1: RAG检索
        query_vector = get_embedding(user_prompt)
        if query_vector is None:
            st.error("问题理解失败。")
            st.stop()
        
        results = collection.query(query_embeddings=[query_vector], n_results=3)
        retrieved_documents = results['documents'][0]
        retrieved_metadatas = results['metadatas'][0]

        # 步骤2: 立即显示检索结果
        with st.expander("🔍 查看检索到的知识片段", expanded=True):
            for i, metadata in enumerate(retrieved_metadatas):
                st.write(f"**片段 {i+1} (来源: {metadata['source']})**")
                st.caption(retrieved_documents[i])
        
        # 步骤3: 流式生成
        thinking_placeholder = st.empty()
        answer_placeholder = st.empty()
        
        reasoning_text = ""
        final_answer = ""
        
        try:
            stream = generate_answer_stream(user_prompt, retrieved_documents, llm_client)
            
            is_thinking_phase = True
            for chunk in stream:
                if not chunk.choices: continue
                delta = chunk.choices[0].delta

                if delta.reasoning_content:
                    reasoning_text += delta.reasoning_content
                    thinking_placeholder.markdown(f"🤔 **AI正在思考...**\n\n---\n{reasoning_text}▌")
                
                elif delta.content:
                    if is_thinking_phase:
                        is_thinking_phase = False
                        thinking_placeholder.expander("🤔 查看AI的思考过程", expanded=False).markdown(reasoning_text)
                    
                    final_answer += delta.content
                    answer_placeholder.markdown(f"🤖 **尼尔AI万事通的回答**\n\n---\n{final_answer}▌")

            if final_answer:
                answer_placeholder.markdown(f"🤖 **尼尔AI万事通的回答**\n\n---\n{final_answer}")

        except Exception as e:
            st.error(f"生成回答时遇到问题：{e}")

    # ✨ 全新、结构化的存储逻辑 ✨
    assistant_message = {
        "role": "assistant",
        "retrieved": {
            "documents": retrieved_documents,
            "metadatas": retrieved_metadatas
        },
        "reasoning": reasoning_text,
        "final_answer": final_answer
    }
    st.session_state.messages.append(assistant_message)