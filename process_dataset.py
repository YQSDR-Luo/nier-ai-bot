import os
import json
import time
from openai import OpenAI

# --- 配置区 ---
# 确保你的API Key已设置为环境变量 SILICONFLOW_API_KEY
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY")

# 输入和输出文件/文件夹路径
INPUT_DIR = "game_scripts"
OUTPUT_FILE = "pod042_dataset.jsonl"

# 用于翻译和生成指令的AI模型
MODEL_NAME = "Qwen/Qwen2.5-32B-Instruct" 

# --- 初始化与检查 ---
if not SILICONFLOW_API_KEY:
    print("错误：未能在系统环境变量中找到 'SILICONFLOW_API_KEY'。")
    exit()

# 初始化LLM客户端
try:
    client = OpenAI(api_key=SILICONFLOW_API_KEY, base_url="https://api.siliconflow.cn/v1")
except Exception as e:
    print(f"初始化OpenAI客户端失败: {e}")
    exit()

# --- 核心AI处理函数 ---

def call_llm(prompt_text, task_description=""):
    """通用LLM调用函数，增加了错误处理和重试机制。"""
    print(f"  > 正在执行任务: {task_description}")
    for attempt in range(3): # 最多重试3次
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt_text}],
                temperature=0.5, # 增加一点创造性，但不过于发散
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"    ! API调用失败 (尝试 {attempt + 1}/3): {e}")
            time.sleep(5) # 等待5秒后重试
    return None

def translate_dialogue(dialogue):
    """第一阶段：将英文对话翻译成中文。"""
    prompt = f"""
请将以下《尼尔：机械纪元》游戏中的英文对话，精准、地道地翻译成简体中文。请只返回翻译后的文本，不要添加任何额外的解释或标签。

英文原文:
"{dialogue}"
"""
    return call_llm(prompt, "翻译Pod对话")

def generate_instruction(pod_response):
    """第二阶段：根据Pod的中文回答，生成一个自然的用户问题。"""
    prompt = f"""
你是一个AI微调数据集的创建者。下面是一句AI助手（以冷静、数据化的机器人风格）的回答。
你的任务是为这句回答，创作一个最可能引发它的、自然的、简短的用户问题或指令。

AI助手的回答:
"{pod_response}"

最可能的用户问题/指令是:
"""
    instruction = call_llm(prompt, "生成用户指令")
    # 清理可能包含的引号
    if instruction and instruction.startswith(('"', '“')) and instruction.endswith(('"', '”')):
        instruction = instruction[1:-1]
    return instruction

# --- 主程序 ---
if __name__ == "__main__":
    print("--- 全自动Pod 042数据集生成脚本启动 ---")

    # 实现断点续传：加载已经处理过的对话
    processed_dialogues = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    # 我们将原始英文对话作为唯一标识符
                    if "source_english" in data:
                        processed_dialogues.add(data["source_english"])
                except json.JSONDecodeError:
                    continue
        print(f"已从输出文件中加载了 {len(processed_dialogues)} 条已处理的记录。")

    # 检查输入目录是否存在
    if not os.path.isdir(INPUT_DIR):
        print(f"错误：输入目录 '{INPUT_DIR}' 不存在。请创建该目录并放入你的.txt文件。")
        exit()

    # 遍历输入目录下的所有txt文件
    source_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.txt')]
    print(f"发现 {len(source_files)} 个源文件需要处理。")

    total_new_entries = 0
    for filename in source_files:
        file_path = os.path.join(INPUT_DIR, filename)
        print(f"\n--- 正在处理文件: {filename} ---")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"  ! 无法读取文件 {filename}: {e}")
            continue

        for i, line in enumerate(lines):
            # 定位Pod 042的对话
            if line.strip().lower().startswith("pod042:"):
                english_dialogue = line.strip()[len("pod042:"):].strip()

                # 跳过空对话或已处理的对话
                if not english_dialogue or english_dialogue in processed_dialogues:
                    continue
                
                print(f"\n处理新对话 (文件 {filename}, 行 {i+1}): {english_dialogue}")

                # 第一阶段：翻译
                translated_dialogue = translate_dialogue(english_dialogue)
                if not translated_dialogue:
                    print("    ! 翻译失败，跳过此条。")
                    continue
                print(f"  > 翻译结果: {translated_dialogue}")
                
                time.sleep(1) # 尊重API频率限制

                # 第二阶段：生成指令
                user_instruction = generate_instruction(translated_dialogue)
                if not user_instruction:
                    print("    ! 指令生成失败，跳过此条。")
                    continue
                print(f"  > 生成的指令: {user_instruction}")
                
                # 构建LLaMA-Factory所需的数据格式
                data_entry = {
                    "conversation": [
                        {"role": "user", "content": user_instruction},
                        {"role": "assistant", "content": translated_dialogue}
                    ],
                    "source_english": english_dialogue # 记录原始英文，用于断点续传
                }

                # 写入JSONL文件
                with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data_entry, ensure_ascii=False) + '\n')
                
                # 更新已处理集合
                processed_dialogues.add(english_dialogue)
                total_new_entries += 1
                print(f"  ✅ 成功生成并保存第 {total_new_entries} 条新数据！")

                time.sleep(1) # 尊重API频率限制

    print(f"\n--- 所有文件处理完毕！总共生成了 {total_new_entries} 条新数据。---")
    print(f"数据集已保存到: {OUTPUT_FILE}")