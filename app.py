from typing import List, Optional, Dict
from pydantic import BaseModel
import asyncio
import uvicorn
import os
import toml
import sys
import logging
import itertools
import json
from httpx import AsyncClient
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_poe.types import ProtocolMessage
from fastapi_poe.client import get_bot_response, get_final_response, QueryRequest

app = FastAPI(title="Poe API Proxy")
security = HTTPBearer()
router = APIRouter()

# 配置加载逻辑 - 优先使用环境变量，如果不存在则尝试从config.toml加载
config = {}
file_path = os.path.abspath(sys.argv[0])
file_dir = os.path.dirname(file_path)
config_path = os.path.join(file_dir, "config.toml")

# 尝试加载配置文件（如果存在）
try:
    if os.path.exists(config_path):
        config = toml.load(config_path)
except Exception as e:
    print(f"无法加载配置文件: {str(e)}")

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("poe-proxy")

# 从环境变量获取API密钥（优先）或配置文件
api_keys_str = os.getenv("POE_API_KEYS", "")
api_keys = set(api_keys_str.split(",") if api_keys_str else config.get("apikey", []))
api_keys = {api_key.strip() for api_key in api_keys if api_key.strip()}

# 从环境变量获取访问令牌（优先）或配置文件
access_tokens_str = os.getenv("ACCESS_TOKENS", "")
access_tokens = set(access_tokens_str.split(",") if access_tokens_str else config.get("accessTokens", []))
access_tokens = {token.strip() for token in access_tokens if token.strip()}

# 获取代理设置和超时时间
proxy_url = os.getenv("PROXY_URL", config.get("proxy", ""))
timeout = int(os.getenv("TIMEOUT", config.get("timeout", 120)))

# 初始化HTTP客户端
if proxy_url:
    proxy = AsyncClient(proxy=proxy_url, timeout=timeout)
else:
    proxy = AsyncClient(timeout=timeout)

# 初始化客户端字典和API密钥循环
client_dict = {}
api_key_cycle = None

# 支持的模型列表
bot_names = {
    "Assistant",
    "GPT-3.5-Turbo", "GPT-3.5-Turbo-16k", "GPT-3.5-Turbo-lnstruct", "GPT-4o", "GPT-4o-128k",
    "GPT-4o-Mini", "GPT-4o-Mini-128k", "ChatGPT-4o-Latest", "ChatGPT-4o-Latest-128k", "GPT-4o-Aug-128k",
    "o1", "o1-mini", "o1-preview",
    "Claude-3.5-Sonnet", "Claude-3.5-Sonnet-200k", "Claude-3.5-Haiku",
    "Claude-3.5-Haiku-200k", "Claude-3.5-Sonnet-June", "Claude-3.5-Sonnet-June-200k", "Claude-3-opus",
    "Claude-3-opus-200k", "Claude-3-Sonnet", "Claude-3-Sonnet-200k", "Claude-3-Haiku", "Claude-3-Haiku-200k",
    "Claude-3.7-Sonnet","Claude-3.7-Sonnet-Reasoning",
    "DeepSeek-R1",
    "Gemini-2.0-Flash", "Gemini-1.5-Pro", "Gemini-1.5-Pro-Search", "Gemini-1.5-Pro-128k", "Gemini-1.5-Pro-2M",
    "Gemini-1.5-Flash",
    "Gemini-1.5-Flash-Search", "Gemini-1.5-Flash-128k", "Gemini-1.5-Flash-1M",
    "Grok-beta", "Grok-2",
    "Qwen-QwQ-32b-preview",
    "Qwen-2.5-Coder-32B-T", "Qwen-2.5-72B-T", "Llama-3.1-405B", "Llama-3.1-405B-T", "Llama-3.1-405B-FP16",
    "Llama-3.1-405B-FW-128k", "Llama-3.1-70B", "Llama-3.1-70B-FP16", "Llama-3.1-70B-T-128k",
    "Llama-3.1-70B-FW-128k", "Llama-3.1-8B", "Llama-3.1-8B-FP16", "Llama-3.1-8B-T-128k", "DALL-E-3",
    "StableDiffusionXL", "StableDiffusion3.5-T", "StableDiffusion3.5-L", "StableDiffusion3", "SD3-Turbo",
    "FLUX-pro", "FLUX-pro-1.1", "FLUX-pro-1.1-T", "FLUX-pro-1.1-ultra", "FLUX-schnell", "FLUX-dev",
    "Luma-Photon", "Luma-Photon-Flash", "Playground-v3", "Ideogram-v2", "Imagen3", "Imagen3-Fast"
}

bot_names_map = {name.lower(): name for name in bot_names}

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


class CompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    skip_system_prompt: Optional[bool] = None
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    logit_bias: Optional[Dict[str, int]] = None
    stop_sequences: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"}
                ],
                "stream": True
            }
        }


async def add_token(token: str):
    global api_key_cycle
    if not token:
        logger.error("Empty token provided")
        return "failed: empty token"

    if token not in client_dict:
        try:
            logger.info(f"Attempting to add apikey: {token[:6]}...")  # 只记录前6位
            request = CompletionRequest(
                model="gpt-3.5-turbo",
                messages=[Message(role="user", content="Please return 'OK'")],
                temperature=0.7
            )
            ret = await get_responses(request, token)
            if ret == "OK":
                client_dict[token] = token
                api_key_cycle = itertools.cycle(client_dict.values())
                logger.info(f"apikey added successfully: {token[:6]}...")
                return "ok"
            else:
                logger.error(f"Failed to add apikey: {token[:6]}..., response: {ret}")
                return "failed"
        except Exception as exception:
            logger.error(f"Failed to connect to poe due to {str(exception)}")
            return f"failed: {str(exception)}"
    else:
        logger.info(f"apikey already exists: {token[:6]}...")
        return "exist"


async def get_responses(request: CompletionRequest, token: str):
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")

    model_lower = request.model.lower()
    if model_lower in bot_names_map:
        request.model = bot_names_map[model_lower]
        message = [
            ProtocolMessage(role=msg.role if msg.role in ["user", "system"] else "bot", content=msg.content)
            for msg in request.messages
        ]
        additional_params = {
            "temperature": request.temperature,
            "skip_system_prompt": request.skip_system_prompt if request.skip_system_prompt is not None else False,
            "logit_bias": request.logit_bias if request.logit_bias is not None else {},
            "stop_sequences": request.stop_sequences if request.stop_sequences is not None else []
        }
        query = QueryRequest(
            query=message,
            user_id="",
            conversation_id="",
            message_id="",
            version="1.0",
            type="query",
            **additional_params
        )
        try:
            return await get_final_response(query, bot_name=request.model, api_key=token, session=proxy)
        except Exception as e:
            logger.error(f"Error in get_final_response: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail=f"Model {request.model} is not supported")


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 如果没有配置访问令牌，则跳过验证
    if access_tokens and credentials.credentials not in access_tokens:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


@router.post("/v1/chat/completions")
@router.post("/chat/completions")
async def create_completion(request: CompletionRequest, token: str = Depends(verify_token)):
    request_id = "chat$poe-to-gpt$-" + token[:6] if token and len(token) > 6 else "chat$poe-to-gpt"

    try:
        # 打印请求参数（隐藏敏感信息）
        safe_request = request.model_dump()
        if "messages" in safe_request:
            safe_request["messages"] = [
                {**msg, "content": msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]}
                for msg in safe_request["messages"]
            ]
        logger.info(f"Request [{request_id}]: {json.dumps(safe_request, ensure_ascii=False)}")

        if not api_key_cycle:
            raise HTTPException(status_code=500, detail="No valid API tokens available")

        model_lower = request.model.lower()
        if model_lower not in bot_names_map:
            raise HTTPException(status_code=400, detail=f"Model {request.model} not found")

        request.model = bot_names_map[model_lower]

        protocol_messages = [
            ProtocolMessage(role=msg.role if msg.role in ["user", "system"] else "bot", content=msg.content)
            for msg in request.messages
        ]
        poe_token = next(api_key_cycle)

        if request.stream:
            async def response_generator():
                total_response = ""
                try:
                    async for partial in get_bot_response(protocol_messages, bot_name=request.model, api_key=poe_token,
                                                          session=proxy):
                        if partial and partial.text:
                            total_response += partial.text
                            chunk = {
                                "id": request_id,
                                "object": "chat.completion.chunk",
                                "created": int(asyncio.get_event_loop().time()),
                                "model": request.model,
                                "choices": [{
                                    "delta": {
                                        "content": partial.text
                                    },
                                    "index": 0,
                                    "finish_reason": None
                                }]
                            }
                            yield f"data: {json.dumps(chunk)}\n\n"

                    # 发送结束标记
                    end_chunk = {
                        "id": request_id,
                        "object": "chat.completion.chunk",
                        "created": int(asyncio.get_event_loop().time()),
                        "model": request.model,
                        "choices": [{
                            "delta": {},
                            "index": 0,
                            "finish_reason": "stop"
                        }]
                    }
                    yield f"data: {json.dumps(end_chunk)}\n\n"
                    yield "data: [DONE]\n\n"

                    # 打印完整的流式响应（限制长度）
                    logger.info(f"Stream Response [{request_id}]: {total_response[:200]}..." if len(
                        total_response) > 200 else total_response)
                except Exception as e:
                    logger.error(f"Error in stream generation for [{request_id}]: {str(e)}")
                    raise

            return StreamingResponse(response_generator(), media_type="text/event-stream")
        else:
            response = await get_responses(request, poe_token)
            response_data = {
                "id": request_id,
                "object": "chat.completion",
                "created": int(asyncio.get_event_loop().time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response
                    },
                    "finish_reason": "stop"
                }]
            }
            # 打印完整响应（限制长度）
            safe_response = {**response_data}
            if len(response) > 200:
                logger.info(f"Response [{request_id}]: {json.dumps(safe_response, ensure_ascii=False)[:200]}...")
            else:
                logger.info(f"Response [{request_id}]: {json.dumps(safe_response, ensure_ascii=False)}")
            return response_data

    except GeneratorExit:
        logger.info(f"GeneratorExit exception caught for request [{request_id}]")
    except Exception as e:
        error_msg = f"Error during response for request [{request_id}]: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
@app.get("/v1/models")
async def list_models(token: str = Depends(verify_token)):
    """返回支持的模型列表"""
    models = []
    for name in bot_names:
        models.append({
            "id": name.lower(),  # 返回小写模型ID
            "object": "model",
            "created": 1677610602,
            "owned_by": "poe",
        })

    return {"object": "list", "data": models}


@app.get("/health")
async def health_check():
    """健康检查端点"""
    if api_key_cycle:
        return PlainTextResponse("OK")
    return PlainTextResponse("No API keys available", status_code=500)


@app.get("/")
async def root():
    """根路径信息页"""
    return PlainTextResponse(
        f"Poe API Proxy - Ready to serve requests. API Keys: {len(client_dict)}, Access Tokens: {len(access_tokens)}"
    )


async def initialize_tokens(tokens: List[str]):
    """初始化API令牌"""
    if not tokens or all(not token for token in tokens):
        logger.error("No API keys found in the configuration.")
        return False
    else:
        for token in tokens:
            if token.strip():
                await add_token(token.strip())
        if not client_dict:
            logger.error("No valid tokens were added.")
            return False
        else:
            global api_key_cycle
            api_key_cycle = itertools.cycle(client_dict.values())
            logger.info(f"Successfully initialized {len(client_dict)} API tokens")
            return True


app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化API令牌"""
    logger.info("Starting Poe API Proxy")
    success = await initialize_tokens(api_keys)
    if not success:
        logger.error("Failed to initialize API tokens. Startup will continue, but requests will fail.")


if __name__ == "__main__":
    # 获取端口，优先使用环境变量
    port = int(os.getenv("PORT", config.get("port", 8080)))

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )