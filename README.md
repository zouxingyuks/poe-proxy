# Poe API 代理

一个功能齐全的Poe API代理服务，可轻松部署到Fly.io。该服务提供与OpenAI API兼容的接口，支持多API密钥轮询和访问令牌认证。

## 目录

- [功能特点](https://poe.com/chat/396zg85y3rr3q8skubq#功能特点)
- [系统要求](https://poe.com/chat/396zg85y3rr3q8skubq#系统要求)
- [快速开始](https://poe.com/chat/396zg85y3rr3q8skubq#快速开始)
- 详细部署步骤
  - [准备工作](https://poe.com/chat/396zg85y3rr3q8skubq#准备工作)
  - [获取源代码](https://poe.com/chat/396zg85y3rr3q8skubq#获取源代码)
  - [创建Fly.io应用](https://poe.com/chat/396zg85y3rr3q8skubq#创建flyio应用)
  - [获取部署令牌](https://poe.com/chat/396zg85y3rr3q8skubq#获取部署令牌)
  - [设置GitHub仓库](https://poe.com/chat/396zg85y3rr3q8skubq#设置github仓库)
  - [配置环境变量](https://poe.com/chat/396zg85y3rr3q8skubq#配置环境变量)
  - [部署应用](https://poe.com/chat/396zg85y3rr3q8skubq#部署应用)
- 使用方法
  - [API参考](https://poe.com/chat/396zg85y3rr3q8skubq#api参考)
  - [示例请求](https://poe.com/chat/396zg85y3rr3q8skubq#示例请求)
- [自定义和扩展](https://poe.com/chat/396zg85y3rr3q8skubq#自定义和扩展)
- [监控与维护](https://poe.com/chat/396zg85y3rr3q8skubq#监控与维护)
- [故障排除](https://poe.com/chat/396zg85y3rr3q8skubq#故障排除)
- [常见问题](https://poe.com/chat/396zg85y3rr3q8skubq#常见问题)

## 功能特点

- 🚀 **简单部署**: 一键部署到Fly.io
- 🔄 **负载均衡**: 支持多个Poe API密钥轮询使用
- 🔒 **安全访问**: 基于令牌的API访问控制
- 🔌 **兼容接口**: 提供与OpenAI API兼容的接口
- 🤖 **多模型支持**: 支持GPT系列、Claude系列等多种模型
- 📊 **自动扩展**: 根据需求自动扩展实例
- 🔄 **自动部署**: 通过GitHub Actions实现持续部署

## 系统要求

- GitHub账户
- Fly.io账户
- Poe API密钥（至少一个）

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/yourusername/poe-proxy.git
cd poe-proxy

# 安装Fly CLI
curl -L https://fly.io/install.sh | sh

# 登录Fly.io
flyctl auth login

# 创建应用
flyctl launch

# 设置环境变量
flyctl secrets set POE_API_KEYS="your-api-key-1,your-api-key-2"
flyctl secrets set ACCESS_TOKENS="your-token-1,your-token-2"

# 部署
flyctl deploy
```

## 详细部署步骤

### 准备工作

1. **注册必要的账户**:

   - [GitHub账户](https://github.com/join)
   - [Fly.io账户](https://fly.io/app/sign-up)

2. **安装Fly CLI**:

   ```bash
   # 在Linux或macOS上
   curl -L https://fly.io/install.sh | sh
   
   # 在Windows上(使用PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

3. **登录Fly.io**:

   ```bash
   flyctl auth login
   ```

### 获取源代码

1. **克隆或下载本仓库**:

   ```bash
   git clone https://github.com/yourusername/poe-proxy.git
   cd poe-proxy
   ```

2. **或者直接从头创建**:

   - 创建项目目录
   - 添加文件: `Dockerfile`, `app.py`, `requirements.txt`, `fly.toml`等
   - 参考本项目的文件内容

### 创建Fly.io应用

1. **初始化Fly.io应用**:

   ```bash
   flyctl launch
   ```

2. **回答交互式问题**:

   - 输入应用名称 (例如: `your-poe-proxy`)
   - 选择区域 (例如: `nrt` (东京) 或 `hkg` (香港))
   - 暂不部署 (选择"No"当询问是否现在部署)

### 获取部署令牌

1. **生成Fly.io API令牌**:

   ```bash
   flyctl auth token
   ```

2. **保存令牌**:
   这个令牌将用于GitHub Actions自动部署，请妥善保存。

### 设置GitHub仓库

1. **创建GitHub仓库**:
   - 前往GitHub创建新仓库
   - 将代码推送到此仓库
2. **设置GitHub Secrets**:
   - 打开仓库设置 > Secrets and variables > Actions
   - 添加以下Secrets:
     - `FLY_API_TOKEN`: 您在上一步获取的Fly.io API令牌
     - `POE_API_KEYS`: 您的Poe API密钥(多个用逗号分隔)
     - `ACCESS_TOKENS`: 访问代理所需的令牌(多个用逗号分隔)

### 配置环境变量

环境变量可以通过GitHub Actions自动设置，也可以手动设置:

**手动设置**:

```bash
# 设置Poe API密钥
flyctl secrets set POE_API_KEYS="your-key-1,your-key-2" --app your-app-name

# 设置访问令牌
flyctl secrets set ACCESS_TOKENS="your-token-1,your-token-2" --app your-app-name
```

**查看已设置的密钥**:

```bash
flyctl secrets list --app your-app-name
```

### 部署应用

**通过GitHub Actions自动部署**:

- 推送代码到GitHub main分支
- 查看GitHub Actions运行状况

**手动部署**:

```bash
flyctl deploy
```

## 使用方法

部署完成后，您的API将可在以下地址访问:

```
https://your-app-name.fly.dev
```

### API参考

#### 健康检查

```
GET /health
```

返回"OK"表示服务运行正常。

#### 聊天完成

```
POST /v1/chat/completions
```

**请求头**:

```
Authorization: Bearer your-access-token
Content-Type: application/json
```

**请求体**:

```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "你好，请介绍一下自己。"}
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**响应**:

```json
{
  "id": "poe-1615478285",
  "object": "chat.completion",
  "created": 1615478285,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！我是一个AI助手，由OpenAI开发..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 120,
    "total_tokens": 135
  }
}
```

#### 获取可用模型

```
GET /v1/models
```

**请求头**:

```
Authorization: Bearer your-access-token
```

**响应**:

```json
{
  "object": "list",
  "data": [
    {
      "id": "gpt-3.5-turbo",
      "object": "model",
      "created": 1677610602,
      "owned_by": "openai"
    },
    {
      "id": "gpt-4",
      "object": "model",
      "created": 1687882411,
      "owned_by": "openai"
    },
    {
      "id": "claude-3-opus-20240229",
      "object": "model",
      "created": 1709251200,
      "owned_by": "anthropic"
    },
    {
      "id": "claude-3-sonnet-20240229",
      "object": "model",
      "created": 1709251200,
      "owned_by": "anthropic"
    }
  ]
}
```

### 示例请求

**使用curl**:

```bash
curl -X POST https://your-app-name.fly.dev/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-access-token" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "告诉我关于量子计算的知识"}
    ],
    "temperature": 0.7
  }'
```

**使用Python**:

```python
import requests
import json

url = "https://your-app-name.fly.dev/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-access-token"
}
data = {
    "model": "gpt-4",
    "messages": [
        {"role": "user", "content": "告诉我关于量子计算的知识"}
    ],
    "temperature": 0.7
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())
```

**使用JavaScript**:

```javascript
fetch("https://your-app-name.fly.dev/v1/chat/completions", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-access-token"
  },
  body: JSON.stringify({
    model: "gpt-4",
    messages: [
      {role: "user", content: "告诉我关于量子计算的知识"}
    ],
    temperature: 0.7
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

## 自定义和扩展

### 修改支持的模型

要修改支持的模型，编辑`app.py`中的`list_models`函数：

```python
@app.get("/v1/models")
async def list_models(authorized: bool = Depends(verify_token)):
    models = [
        # 添加或移除模型定义
        {
            "id": "your-new-model",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "provider"
        },
    ]
    
    return {"object": "list", "data": models}
```

### 添加更多功能

您可以通过修改`app.py`文件添加更多功能，例如：

- 实现流式响应
- 添加更多API端点
- 集成更多模型提供商

## 监控与维护

### 查看日志

```bash
flyctl logs --app your-app-name
```

### 检查应用状态

```bash
flyctl status --app your-app-name
```

### 扩展应用实例

```bash
flyctl scale count 2 --app your-app-name
```

### 设置警报

```bash
flyctl monitor create --app your-app-name
```

## 故障排除

### 部署失败

**问题**: GitHub Actions部署失败
 **解决方案**:

- 检查`FLY_API_TOKEN`是否正确设置
- 查看GitHub Actions日志了解详细错误信息
- 尝试手动部署并查看错误消息

### 应用运行但无法访问

**问题**: 应用已部署但无法访问
 **解决方案**:

- 检查应用状态: `flyctl status --app your-app-name`
- 查看日志: `flyctl logs --app your-app-name`
- 确认应用已分配公共IP: `flyctl ips list --app your-app-name`

### API密钥问题

**问题**: API返回401或403错误
 **解决方案**:

- 确认环境变量已正确设置: `flyctl secrets list --app your-app-name`
- 验证请求中的访问令牌是否正确
- 检查API密钥是否有效

## 常见问题

**Q: 可以使用多少个API密钥?**
 A: 您可以添加任意数量的API密钥，系统将自动轮询使用。

**Q: 如何修改应用的区域?**
 A: 编辑`fly.toml`文件中的`primary_region`设置，然后重新部署。

**Q: 应用会自动扩展吗?**
 A: 是的，Fly.io会根据流量自动扩展实例。您也可以通过`flyctl scale`命令手动调整。

**Q: 如何更新环境变量?**
 A: 使用`flyctl secrets set`命令更新环境变量，例如:

```bash
flyctl secrets set POE_API_KEYS="new-key-1,new-key-2" --app your-app-name
```

**Q: 可以连接自定义域名吗?**
 A: 是的，使用以下命令:

```bash
flyctl certs create your-domain.com --app your-app-name
```

------

## 贡献指南

欢迎提交问题报告和功能建议。如需贡献代码，请先Fork本仓库，然后提交Pull Request。

## 许可证

本项目采用MIT许可证。详见[LICENSE](./LICENSE)文件。

------

**注意**: 使用本项目时请确保遵守Poe API的服务条款和使用政策。