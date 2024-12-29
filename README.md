# LanChain+LangFlow+LineBot串接並部署到AZURE


## 簡介

## 目錄
- [LanChain+LangFlow+LineBot串接並部署到AZURE](#lanchainlangflowlinebot串接並部署到azure)
  - [簡介](#簡介)
  - [目錄](#目錄)
  - [操作步驟](#操作步驟)
    - [STEP1：建立並修改env檔](#step1建立並修改env檔)
    - [STEP2：撰寫`function_app.py`](#step2撰寫function_apppy)
    - [STEP3：撰寫`requirements.txt`](#step3撰寫requirementstxt)
    - [STEP4：請先在地端點擊F5進行測試，測試無誤後再部署到AzureFunction](#step4請先在地端點擊f5進行測試測試無誤後再部署到azurefunction)
    - [STEP5：進入Azure Portal，點擊建立資源\>容器\>Container Registry](#step5進入azure-portal點擊建立資源容器container-registry)
    - [STEP6：完成後，進入剛才建立的容器登錄\>設定\>存取金鑰](#step6完成後進入剛才建立的容器登錄設定存取金鑰)
    - [STEP7：開啟cmd，輸入以下指令](#step7開啟cmd輸入以下指令)
    - [STEP8：確認是否有出現這畫面，表示登入成功](#step8確認是否有出現這畫面表示登入成功)
    - [STEP9：打包lanflow的DockerImage](#step9打包lanflow的dockerimage)
    - [STEP10：這樣就代表打包好了](#step10這樣就代表打包好了)
    - [STEP11：執行標記並推送映像檔](#step11執行標記並推送映像檔)
    - [STEP12：確認是否推送成功](#step12確認是否推送成功)
    - [STEP13：建立Azure Storage](#step13建立azure-storage)
    - [STEP14：執行以下指令建立容器執行個體](#step14執行以下指令建立容器執行個體)
    - [STEP15：執行腳本掛載AZURE儲存庫到Windows地端](#step15執行腳本掛載azure儲存庫到windows地端)


## 操作步驟

 > [!note] 
 > AZURE FUNCTION建立可參考這一篇
 > https://github.com/Mark850409/20231217_AzureFunctionAPI
 > AZURE FUNCTION串接LINEBOT可參考這一篇
 > https://github.com/Mark850409/20231224_AzureLINEBOTAPI

### STEP1：建立並修改env檔

請自行在專案下建立`.env`，按照以下範例進行調整

```
#######################################
# API配置
#######################################
# API設置相關，根據自己的實際情況進行調整
PORT=8012

#######################################
# LangFlow配置
#######################################
LANGFLOW_BASE_URL="<自己的LANGFLOW URL>"

#######################################
# LINEBOT配置
#######################################
CHANNEL_ACCESS_TOKEN="<自己的CHANNEL_ACCESS_TOKEN>"
CHANNEL_SECRET="<自己的CHANNEL_SECRET>"
```

### STEP2：撰寫`function_app.py`

```python
import azure.functions as func
import logging
import json
import requests
# LineBotApi
from linebot import LineBotApi, WebhookHandler  
from linebot.exceptions import InvalidSignatureError  
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,JoinEvent,FollowEvent
)
# 環境變數相關
import os
from dotenv import load_dotenv  # pip install python-dotenv

# 設置日誌模板
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 載入 .env 檔案
load_dotenv()

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

#取得LINEBOT的CHANNEL_SECRET&CHANNEL_ACCESS_TOKEN&USER_ID
LANGFLOW_BASE_URL = os.getenv("LANGFLOW_BASE_URL") 
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

if not LANGFLOW_BASE_URL or not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    logger.error("環境變數缺失，請確認 .env 檔案設置是否正確！")
    raise ValueError("必要的環境變數未設置！")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    # 上線測試，請使用這段
    try:
        signature = req.headers['x-line-signature']
        logging.info("signature: " + signature)

        # 取得 LINE body內容
        body = req.get_body().decode("utf-8")
        logging.info("Request body: " + body)

        # handle webhook body
        handler.handle(body, signature)
        return func.HttpResponse("OK", status_code=200)
    except InvalidSignatureError:
        logging.error("Invalid signature error")
        return func.HttpResponse("Invalid signature", status_code=400)
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        return func.HttpResponse("Internal server error", status_code=500)



#文字訊息觸發點
@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
   #取得文字內容
    input_text = event.message.text.strip()
    if input_text:
        try:
            result = call_api(input_text)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=result)
            )
        except Exception as e:
            logger.error(f"API 呼叫失敗: {e}")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法處理您的請求，請稍後再試！")
            )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="您輸入的內容有誤，請重新嘗試！")
        )

    
#第一次加入好友觸發點
@handler.add(JoinEvent)
def handle_join(event):
    user_id = event.source.user_id  
    profile = line_bot_api.get_profile(user_id)  
    user_name = profile.display_name  
    text=''
    text+=f"{user_name}您好!\n"
    text+="我是關於韓國團體的十萬個為什麼\n"
    text+="感謝您加入好友😘\n\n"
    text+="您可以向我詢問了解韓國團體相關問題，我會盡可能提供回覆說明"
    line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=text)
        )
    
#封鎖後重新加入好友觸發點
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id  
    profile = line_bot_api.get_profile(user_id)  
    user_name = profile.display_name  
    text=''
    text+=f"{user_name}您好!\n"
    text+="我是關於韓國團體的十萬個為什麼\n"
    text+="感謝您加入好友😘\n\n"
    text+="您可以向我詢問了解韓國團體相關問題，我會盡可能提供回覆說明"
    line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=text)
        )

# 1、呼叫LangFlow API
def call_api(input_text):
    
    url = f"{LANGFLOW_BASE_URL}api/v1/run/ragflow?stream=false"
    headers = {"Content-Type": "application/json"}
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

    # 2、發送 POST 請求進行測試
    response = requests.post(url, headers=headers, data=json.dumps(data))
    logger.info(f"輸出響應內容是: {response}\n")
    # 3、檢查響應狀態碼
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

if __name__ == "__main__":
    logger.info("LINE Bot Azure Function 已啟動！")
```

### STEP3：撰寫`requirements.txt`

```
azure-functions
python-dotenv
requests
line-bot-sdk
Flask
```

### STEP4：請先在地端點擊F5進行測試，測試無誤後再部署到AzureFunction


### STEP5：進入Azure Portal，點擊建立資源>容器>Container Registry

建立自己的容器存放庫

![alt text](https://raw.githubusercontent.com/Mark850409/20241227_LangFlowWithAzureBot/refs/heads/master/images/image.png)

![alt text](https://raw.githubusercontent.com/Mark850409/20241227_LangFlowWithAzureBot/refs/heads/master/images/image-1.png)

![alt text](https://raw.githubusercontent.com/Mark850409/20241227_LangFlowWithAzureBot/refs/heads/master/images/image-2.png)


### STEP6：完成後，進入剛才建立的容器登錄>設定>存取金鑰

請先將紅框部分先記下來，等等會使用到

![](https://raw.githubusercontent.com/Mark850409/20241227_LangFlowWithAzureBot/refs/heads/master/images/image-3.png)


### STEP7：開啟cmd，輸入以下指令

```docker
docker login langflowbot.azurecr.io -u LangFlowBot
```

![alt text](https://raw.githubusercontent.com/Mark850409/20241227_LangFlowWithAzureBot/refs/heads/master/images/image-5.png)

### STEP8：確認是否有出現這畫面，表示登入成功

![alt text](https://raw.githubusercontent.com/Mark850409/20241227_LangFlowWithAzureBot/refs/heads/master/images/image-6.png)


### STEP9：打包lanflow的DockerImage

```docker
docker build -t langflow:1.0 . 
```

### STEP10：這樣就代表打包好了


![alt text](https://raw.githubusercontent.com/Mark850409/20241227_LangFlowWithAzureBot/refs/heads/master/images/image-4.png)

### STEP11：執行標記並推送映像檔

```docker
docker tag langflow:1.0 langflowbot.azurecr.io/langflow:1.0

docker push langflowbot.azurecr.io/langflow:1.0
```

### STEP12：確認是否推送成功

![alt text](https://raw.githubusercontent.com/Mark850409/20241227_LangFlowWithAzureBot/refs/heads/master/images/image-7.png)


### STEP13：建立Azure Storage

按照以下資訊填入

![alt text](https://raw.githubusercontent.com/Mark850409/20241227_LangFlowWithAzureBot/refs/heads/master/images/image-8.png)

無須更動設定，直接點選建立

![alt text](https://raw.githubusercontent.com/Mark850409/20241227_LangFlowWithAzureBot/refs/heads/master/images/image-9.png)

### STEP14：執行以下指令建立容器執行個體

 > [!note] 
 > 請在地端先安裝AZURE CLI指令，或者進入AZURE CLOUDSHELL操作

 ```bash
# 列出可用訂閱
az account list --output table

# 切換訂閱
az account set --subscription <SUBSCRIPTION_ID>

# 檢查資源群組名稱
az group list --output table

# 建立容器執行個體
az container create \
  --resource-group AIChatBot \
  --name langflowchatbot \
  --cpu 1 \
  --memory 2 \
  --ports 7860 \
  --ip-address Public \
  --dns-name-label mylangflowchatbot \
  --image langflowbot.azurecr.io/langflow:1.0 \
  --azure-file-volume-account-name <改成自己的儲存庫名稱> \
  --azure-file-volume-account-key <改成自己的金鑰> \
  --azure-file-volume-share-name <改成自己的儲存庫名稱> \
  --azure-file-volume-mount-path <改成自己的要綁定的路徑>

# 進入容器，檢查目錄是否綁定成功
az container exec --resource-group AIChatBot --name langflowchatbot --exec-command "/bin/bash"
ls /mnt/data
 ```

 ### STEP15：執行腳本掛載AZURE儲存庫到Windows地端

執行這隻腳本前，請先打開此檔案更改金鑰

```powershell
azure_storage.bat
```