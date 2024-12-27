# 使用 API 接口進行調用
import requests
import json
import logging
# 環境變數相關
import os
from dotenv import load_dotenv  # pip install python-dotenv

# 設置日誌模板
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 載入 .env 檔案
load_dotenv()

# API設置相關，根據自己的實際情況進行調整
LANGFLOW_BASE_URL = os.getenv("LANGFLOW_BASE_URL") 
logger.info(f"LANGFLOW_BASE_URL: {LANGFLOW_BASE_URL}")

if not LANGFLOW_BASE_URL:
    logger.error("LANGFLOW_BASE_URL is not set. Check your .env file.")
    raise ValueError("LANGFLOW_BASE_URL is not set")

# 1、呼叫LangFlow API
url = f"{LANGFLOW_BASE_URL}api/v1/run/ragflow?stream=false"
headers = {"Content-Type": "application/json"}

# 2、發送 POST 請求進行測試
def call_api(input_text):
    data = {
        "input_value": input_text,
        "output_type": "chat",
        "input_type": "chat",
        "ChatInput-AEgML": {
            "background_color": "",
            "chat_icon": "",
            "files": "",
            "input_value": "BLACKPINK成員有誰?",
            "sender": "User",
            "sender_name": "User",
            "session_id": "",
            "should_store_message": True,
            "text_color": ""
        },
        "ParseData-5gm6a": {
            "sep": "\n",
            "template": "{text}"
        },
        "Prompt-mXovt": {
            "context": "",
            "question": "",
            "template": "{context}\n\n---\n\nGiven the context above, answer the question as best as possible.\n\nQuestion: {question}\n\nAnswer: "
        },
        "SplitText-NVr6U": {
            "chunk_overlap": 200,
            "chunk_size": 1000,
            "separator": "\n"
        },
        "ChatOutput-cpZXc": {
            "background_color": "",
            "chat_icon": "",
            "data_template": "{text}",
            "input_value": "",
            "sender": "Machine",
            "sender_name": "AI",
            "session_id": "",
            "should_store_message": True,
            "text_color": ""
        },
        "OpenAIEmbeddings-EONzf": {
            "chunk_size": 1000,
            "client": "",
            "default_headers": {},
            "default_query": {},
            "deployment": "",
            "dimensions": None,
            "embedding_ctx_length": 1536,
            "max_retries": 3,
            "model": "text-embedding-3-small",
            "model_kwargs": {},
            "openai_api_base": "",
            "openai_api_key": "",
            "openai_api_type": "",
            "openai_api_version": "",
            "openai_organization": "",
            "openai_proxy": "",
            "request_timeout": None,
            "show_progress_bar": False,
            "skip_empty": False,
            "tiktoken_enable": True,
            "tiktoken_model_name": ""
        },
        "Chroma-gPLzo": {
            "allow_duplicates": False,
            "chroma_server_cors_allow_origins": "",
            "chroma_server_grpc_port": None,
            "chroma_server_host": "",
            "chroma_server_http_port": None,
            "chroma_server_ssl_enabled": False,
            "collection_name": "KPOP",
            "limit": None,
            "number_of_results": 10,
            "persist_directory": "KPOP_1227",
            "search_query": "",
            "search_type": "Similarity"
        },
        "Directory-zgZD3": {
            "depth": 0,
            "load_hidden": False,
            "max_concurrency": 2,
            "path": "/mnt/data",
            "recursive": False,
            "silent_errors": False,
            "types": "",
            "use_multithreading": False
        },
        "OpenAIEmbeddings-5fBe2": {
            "chunk_size": 1000,
            "client": "",
            "default_headers": {},
            "default_query": {},
            "deployment": "",
            "dimensions": None,
            "embedding_ctx_length": 1536,
            "max_retries": 3,
            "model": "text-embedding-3-small",
            "model_kwargs": {},
            "openai_api_base": "",
            "openai_api_key": "",
            "openai_api_type": "",
            "openai_api_version": "",
            "openai_organization": "",
            "openai_proxy": "",
            "request_timeout": None,
            "show_progress_bar": False,
            "skip_empty": False,
            "tiktoken_enable": True,
            "tiktoken_model_name": ""
        },
        "Chroma-XecOe": {
            "allow_duplicates": False,
            "chroma_server_cors_allow_origins": "",
            "chroma_server_grpc_port": None,
            "chroma_server_host": "",
            "chroma_server_http_port": None,
            "chroma_server_ssl_enabled": False,
            "collection_name": "KPOP",
            "limit": None,
            "number_of_results": 10,
            "persist_directory": "KPOP_1227",
            "search_query": "",
            "search_type": "Similarity"
        },
        "OllamaModel-tvBgy": {
            "base_url": "",
            "format": "",
            "input_value": "",
            "metadata": {},
            "mirostat": "Disabled",
            "mirostat_eta": None,
            "mirostat_tau": None,
            "model_name": "llama3.2:latest",
            "num_ctx": None,
            "num_gpu": None,
            "num_thread": None,
            "repeat_last_n": None,
            "repeat_penalty": None,
            "stop_tokens": "",
            "stream": False,
            "system": "",
            "system_message": "System Promt",
            "tags": "",
            "temperature": 0.5,
            "template": "",
            "tfs_z": None,
            "timeout": None,
            "top_k": None,
            "top_p": None,
            "verbose": False
        }
    }

    # 3、發送 POST 請求進行測試
    response = requests.post(url, headers=headers, data=json.dumps(data))
    logger.info(f"輸出響應內容是: {response}\n")
    # 檢查響應狀態碼
    if response.status_code == 200:
        try:
            logger.info(f"輸出響應內容是: {response.status_code}\n")
            logger.info(f"輸出響應內容是: {response.json()}\n")
            # 解析具體回覆的內容
            content = response.json()['outputs'][0]['outputs'][0]['results']['message']['data']['text']
            # 確保正確顯示中文，使用 print 並避免轉義
            print(json.dumps(content, ensure_ascii=False))  # 正確顯示中文
            return content
        except requests.exceptions.JSONDecodeError:
            # 響應不是 JSON 格式
            logger.info("響應內容不是有效的 JSON")
    else:
        logger.info(f"請求失敗，狀態碼為 {response.status_code}")

# 循環訊息測試
if __name__ == "__main__":
    print("輸入 'exit' 可退出程式")
    while True:
        # 提示使用者輸入測試文字
        input_text = input("請輸入您的問題：")
        if input_text.lower() == "exit":
            print("程式結束。")
            break
        call_api(input_text)