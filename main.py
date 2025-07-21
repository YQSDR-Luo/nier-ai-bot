# 导入os库，我们的文件操作全靠它
import os

# --- 准备工作 ---
# 知识库文件夹的名字，确保它和你的文件夹名字完全一样
KNOWLEDGE_BASE_DIR = "NieR-Automata-RAG-KB"

# 同样，我们先获取当前项目的根目录
project_root = os.path.dirname(os.path.abspath(__file__))

# 然后，拼接出知识库文件夹的完整路径
knowledge_base_path = os.path.join(project_root, KNOWLEDGE_BASE_DIR)

# --- 核心代码：使用 os.walk 遍历所有文件 ---
if not os.path.exists(knowledge_base_path):
    print(f"错误：找不到知识库文件夹 '{knowledge_base_path}'！")
    print("请确保你的项目结构是这样的：")
    print("nier_ai_bot/")
    print("├── main.py")
    print("└── NieR-Automata-RAG-KB/")
else:
    print(f"成功找到知识库，路径是：{knowledge_base_path}\n")
    
    # 创建一个列表，用来存放我们读出来的所有文档
    all_documents = []

    # 这就是我们的“探险家”：os.walk()！
    # 它会遍历 knowledge_base_path 下的每一个文件夹
    # for循环每次会返回三个东西：
    # 1. current_path: 当前正在访问的这个文件夹的路径
    # 2. sub_folders: 这个文件夹里包含的子文件夹的名字列表
    # 3. files_in_folder: 这个文件夹里包含的文件的名字列表
    for current_path, sub_folders, files_in_folder in os.walk(knowledge_base_path):
        print(f"--- 正在探索文件夹: {current_path} ---")
        
        # 对当前文件夹里的每一个文件名进行处理
        for filename in files_in_folder:
            # 我们只关心 .txt 和 .md 文件，忽略其他可能存在的文件（比如Mac自动生成的.DS_Store）
            # filename.endswith(('.txt', '.md')) 这个判断非常有用！
            if filename.endswith(('.txt', '.md')):
                
                # 拼接出这个文件的完整路径
                file_path = os.path.join(current_path, filename)
                
                print(f"  正在读取文件: {filename}")
                
                # 使用标准、安全的方式读取文件内容
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        
                        # 这次我们存储更多信息！除了内容，还把文件的来源和分类也存进去
                        # 这样做的好处是，以后AI回答问题时，我们可以告诉用户答案出自哪个章节
                        document = {
                            "source_file": filename,  # 文件名
                            "content": file_content,  # 文件内容
                            "category": os.path.basename(current_path) # 文件所在的文件夹名，作为分类
                        }
                        all_documents.append(document)
                except Exception as e:
                    print(f"    读取文件 {filename} 时发生错误: {e}")

    # --- 验证结果 ---
    print("\n" + "="*30)
    print("所有文件探索和读取完毕！")
    print(f"总共加载了 {len(all_documents)} 个文档。")
    
    if all_documents:
        print("\n随机抽样一个文档看看效果：")
        # 我们可以看看中间的某个文档，来验证子文件夹是否被正确读取
        sample_doc = all_documents[len(all_documents) // 2] 
        print(f"  文档分类: {sample_doc['category']}")
        print(f"  来源文件: {sample_doc['source_file']}")
        print(f"  内容预览: {sample_doc['content'][:150]}...")