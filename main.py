import os
import requests
import chromadb
from openai import OpenAI

# --- 准备工作 (环境变量读取) ---
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY")
if not SILICONFLOW_API_KEY:
    print("错误：未能在系统环境变量中找到 'SILICONFLOW_API_KEY'。")
    exit()

project_root = os.path.dirname(os.path.abspath(__file__))

# --- 核心函数 (get_embedding 保持不变) ---
def get_embedding(text_chunk):
    # ... (此函数内容与之前完全相同，为节省篇幅此处省略) ...
    url = "https://api.siliconflow.cn/v1/embeddings"
    model_name = "BAAI/bge-m3"
    headers = { "Authorization": f"Bearer {SILICONFLOW_API_KEY}", "Content-Type": "application/json" }
    payload = { "model": model_name, "input": text_chunk }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['data'][0]['embedding']
        else:
            return None
    except Exception as e:
        return None

# --- ✨✨✨ 最终版流式生成函数（保持不变） ✨✨✨ ---
def generate_answer_stream_with_reasoning(query, retrieved_chunks):
    client = OpenAI(api_key=SILICONFLOW_API_KEY, base_url="https://api.siliconflow.cn/v1")
    context = "\n\n---\n\n".join(retrieved_chunks)
    prompt = f"""
请你扮演一个《尼尔：机械纪元》的资深专家。
你的任务是根据下面提供的上下文信息，简洁、清晰地回答用户的问题。
在回答前，请先进行一步思考（Reasoning），分析上下文中的哪些信息可以用来回答问题。
然后，根据你的思考，给出最终的答案。
【上下文信息】:
{context}
【用户的问题】:
{query}
"""
    model_name = "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B" 
    try:
        stream = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        return stream
    except Exception as e:
        print(f"生成答案过程中发生严重错误: {e}")
        return None

# --- 主程序入口 (最终增强版，带状态管理！) ---
if __name__ == "__main__":
    db_path = os.path.join(project_root, "nier_vector_db")
    client = chromadb.PersistentClient(path=db_path)
    collection_name = "nier_automata_kb"
    collection = client.get_or_create_collection(name=collection_name)

    if collection.count() == 0:
        print("数据库为空，请先运行一次带有初始化功能的脚本来填充数据。")
        exit()
    else:
        print(f"数据库 '{collection_name}' 中已存在 {collection.count()} 个知识块。")

    query_text = "游戏有哪些结局？"
    print("\n" + "="*30)
    print(f"用户问题: {query_text}")
    
    query_vector = get_embedding(query_text)
    
    if query_vector:
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=3
        )
        retrieved_documents = results['documents'][0]
        
        print("\n检索到的相关信息:")
        for i, doc in enumerate(retrieved_documents):
            print(f"  - [片段{i+1}]: {doc[:80]}...")
            
        stream = generate_answer_stream_with_reasoning(query_text, retrieved_documents)
        
        if stream:
            print("\n" + "="*30)
            
            # ✨✨✨ 引入状态管理，清晰分割思考与回答 ✨✨✨
            # current_phase 可以是 None, 'reasoning', 或 'answering'
            current_phase = None

            for chunk in stream:
                if not chunk.choices:
                    continue
                
                delta = chunk.choices[0].delta

                # 捕获并打印推理内容
                if delta.reasoning_content:
                    # 如果这是思考的第一个数据块
                    if current_phase != 'reasoning':
                        current_phase = 'reasoning'
                        print("🤔 AI正在思考...")
                    print(delta.reasoning_content, end="", flush=True)
                
                # 捕获并打印最终回答内容
                elif delta.content:
                    # 如果这是回答的第一个数据块
                    if current_phase != 'answering':
                        # 如果之前是在思考，就打印一个分割线，让格式更清晰
                        if current_phase == 'reasoning':
                            print("\n" + "-"*20)
                        current_phase = 'answering'
                        print("🤖 尼尔AI万事通的回答:")
                    print(delta.content, end="", flush=True)
            
            print() # 结束时换行
            
    else:
        print("问题向量化失败，无法进行查询。")