import os
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union

from fastapi import FastAPI, Request, Response, HTTPException, Depends, Header
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("poe-proxy")

# 创建FastAPI应用
app = FastAPI(title="Poe API Proxy")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 从环境变量获取配置
POE_API_KEYS = os.getenv("POE_API_KEYS", "").split(",") if os.getenv("POE_API_KEYS") else []
ACCESS_TOKENS = os.getenv("ACCESS_TOKENS", "").split(",") if os.getenv("ACCESS_TOKENS") else []
POE_API_URL = "https://api.poe.com/bot/api/query"


# 数据模型
class Message(BaseModel):
    role: str
    content: str


class PoeRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False


class ErrorResponse(BaseModel):
    error: str


# 身份验证依赖
async def verify_token(authorization: Optional[str] = Header(None)):
    if not ACCESS_TOKENS:  # 如果未设置访问令牌，跳过验证
        return True

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization

    if token not in ACCESS_TOKENS:
        raise HTTPException(status_code=403, detail="Invalid access token")

    return True


# 轮询API密钥
current_key_index = 0


def get_poe_api_key():
    global current_key_index
    if not POE_API_KEYS:
        raise HTTPException(status_code=500, detail="No POE API keys configured")

    key = POE_API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(POE_API_KEYS)
    return key


# 健康检查端点
@app.get("/health", response_class=PlainTextResponse)
async def health_check():
    return "OK"


# 主要API代理端点
@app.post("/v1/chat/completions")
async def chat_completions(request_data: PoeRequest, authorized: bool = Depends(verify_token)):
    try:
        api_key = get_poe_api_key()

        # 将请求转换为Poe API格式
        poe_messages = []
        for msg in request_data.messages:
            role = "user" if msg.role == "user" else "assistant"
            poe_messages.append({"role": role, "content": msg.content})

        poe_request = {
            "model": request_data.model,
            "messages": poe_messages,
            "temperature": request_data.temperature,
            "max_tokens": request_data.max_tokens,
        }

        # 调用Poe API
        async with httpx.AsyncClient(timeout=120.0) as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Sending request to Poe API for model: {request_data.model}")
            start_time = time.time()

            response = await client.post(
                POE_API_URL,
                json=poe_request,
                headers=headers
            )

            elapsed_time = time.time() - start_time
            logger.info(f"Received response from Poe API in {elapsed_time:.2f}s")

            if response.status_code != 200:
                logger.error(f"Poe API error: {response.status_code} - {response.text}")
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": f"Poe API error: {response.text}"}
                )

            # 处理响应
            poe_response = response.json()

            # 构建符合OpenAI格式的响应
            result = {
                "id": f"poe-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request_data.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": poe_response.get("response", "")
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": poe_response.get("prompt_tokens", 0),
                    "completion_tokens": poe_response.get("completion_tokens", 0),
                    "total_tokens": poe_response.get("prompt_tokens", 0) + poe_response.get("completion_tokens", 0)
                }
            }

            return result

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )


# 模型列表端点
@app.get("/v1/models")
async def list_models(authorized: bool = Depends(verify_token)):
    models = [
        {
            "id": "gpt-3.5-turbo",
            "object": "model",
            "created": 1677610602,
            "owned_by": "openai",
        },
        {
            "id": "gpt-4",
            "object": "model",
            "created": 1687882411,
            "owned_by": "openai",
        },
        {
            "id": "claude-3-opus-20240229",
            "object": "model",
            "created": 1709251200,
            "owned_by": "anthropic",
        },
        {
            "id": "claude-3-sonnet-20240229",
            "object": "model",
            "created": 1709251200,
            "owned_by": "anthropic",
        }
    ]

    return {"object": "list", "data": models}


# 根路径
@app.get("/", response_class=PlainTextResponse)
async def root():
    return f"Poe API Proxy - Ready to serve requests. API Keys: {len(POE_API_KEYS)}, Access Tokens: {len(ACCESS_TOKENS)}"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)