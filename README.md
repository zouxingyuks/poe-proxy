# Poe API 代理

一个功能齐全的 Poe API 代理服务，提供兼容 OpenAI 的接口访问各种 AI 模型，可轻松部署到 Fly.io。

## 目录

- [功能特点](#功能特点)
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [详细部署步骤](#详细部署步骤)
  - [准备工作](#准备工作)
  - [获取源代码](#获取源代码)
  - [创建Fly.io应用](#创建flyio应用)
  - [获取部署令牌](#获取部署令牌)
  - [设置GitHub仓库](#设置github仓库)
  - [配置环境变量](#配置环境变量)
  - [配置自定义域名](#配置自定义域名)
  - [部署应用](#部署应用)
- [使用方法](#使用方法)
  - [API参考](#api参考)
  - [示例请求](#示例请求)
- [文件结构](#文件结构)
- [自定义和扩展](#自定义和扩展)
- [监控与维护](#监控与维护)
- [故障排除](#故障排除)
- [常见问题](#常见问题)

## 功能特点

- 🚀 **简单部署**: 一键部署到 Fly.io
- 🔄 **负载均衡**: 支持多个 Poe API 密钥轮询使用
- 🔒 **安全访问**: 基于令牌的 API 访问控制
- 🔌 **兼容接口**: 提供与 OpenAI API 兼容的接口
- 🤖 **多模型支持**: 支持 GPT、Claude、Gemini、Llama 等多种模型
- 🌐 **自定义域名**: 支持绑定您自己的域名
- 📊 **自动扩展**: 根据需求自动扩展实例
- ⚡ **流式响应**: 支持 SSE 流式输出

## 系统要求

- GitHub 账户
- Fly.io 账户
- Poe API 密钥（至少一个）
- 域名（可选，用于自定义域名功能）

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/yourusername/poe-proxy.git
cd poe-proxy

# 安装 Fly CLI
curl -L https://fly.io/install.sh | sh

# 登录 Fly.io
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

   - [GitHub 账户](https://github.com/join)
   - [Fly.io 账户](https://fly.io/app/sign-up)

2. **安装 Fly CLI**:

   ```bash
   # 在 Linux 或 macOS 上
   curl -L https://fly.io/install.sh | sh
   
   # 在 Windows 上(使用 PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

3. **登录 Fly.io**:

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
   - 添加必要文件: `Dockerfile`, `app.py`, `requirements.txt`, `fly.toml` 等
   - 可以参考本项目的文件内容

### 创建 Fly.io 应用

1. **初始化 Fly.io 应用**:

   ```bash
   flyctl launch
   ```

2. **回答交互式问题**:

   - 输入应用名称 (例如: `your-poe-proxy`)
   - 选择区域 (例如: `nrt` (东京) 或 `hkg` (香港))
   - 暂不部署 (选择"No"当询问是否现在部署)

### 获取部署令牌

1. **生成 Fly.io API 令牌**:

   ```bash
   flyctl auth token
   ```

2. **保存令牌**:
   这个令牌将用于 GitHub Actions 自动部署，请妥善保存。

### 设置 GitHub 仓库

1. **创建 GitHub 仓库**:
   - 前往 GitHub 创建新仓库
   - 将代码推送到此仓库

2. **设置 GitHub Secrets**:
   - 打开仓库设置 > Secrets and variables > Actions
   - 添加以下 Secrets:
     - `FLY_API_TOKEN`: 您在上一步获取的 Fly.io API 令牌
     - `POE_API_KEYS`: 您的 Poe API 密钥(多个用逗号分隔)
     - `ACCESS_TOKENS`: 访问代理所需的令牌(多个用逗号分隔)

### 配置环境变量

环境变量可以通过 GitHub Actions 自动设置，也可以手动设置:

**手动设置**:

```bash
# 设置 Poe API 密钥
flyctl secrets set POE_API_KEYS="your-key-1,your-key-2" --app your-app-name

# 设置访问令牌
flyctl secrets set ACCESS_TOKENS="your-token-1,your-token-2" --app your-app-name

# 设置代理（可选）
flyctl secrets set PROXY_URL="http://your-proxy:port" --app your-app-name

# 设置超时时间（可选，默认120秒）
flyctl secrets set TIMEOUT="180" --app your-app-name
```

**查看已设置的密钥**:

```bash
flyctl secrets list --app your-app-name
```

### 配置自定义域名

您可以为您的 Poe API 代理设置自定义域名，这样可以通过您自己的域名访问服务。

1. **设置 GitHub Variable**:

   - 打开仓库设置 > Secrets and variables > Actions
   - 切换到 "Variables" 选项卡
   - 添加一个新变量:
     - 名称: `CUSTOM_DOMAIN`
     - 值: 您的域名 (例如: `api.example.com`)

2. **DNS 配置**:
   部署完成后，您需要在您的域名注册商或 DNS 提供商处添加 DNS 记录:

   - 添加一条 CNAME 记录，指向您的 Fly.io 应用域名
   - 例如: `CNAME  api.example.com  →  your-app-name.fly.dev`

3. **验证域名**:

   - 部署成功后，Fly.io 会自动为您的域名申请 SSL 证书
   - 您可以在 Fly.io 控制台的 "Certificates" 标签中查看证书状态
   - DNS 配置生效后，证书将自动颁发（这可能需要几分钟到几小时）

4. **验证配置**:

   ```bash
   # 查看域名状态
   flyctl domains list --app your-app-name
   
   # 查看证书状态
   flyctl certs list --app your-app-name
   ```

### 部署应用

**通过 GitHub Actions 自动部署**:

- 推送代码到 GitHub master 分支
- 查看 GitHub Actions 运行状况

**手动部署**:

```bash
flyctl deploy
```

## 使用方法

部署完成后，您的 API 将可在以下地址访问:

```
https://your-app-name.fly.dev
```

如果您配置了自定义域名，也可以通过您的域名访问:

```
https://your-custom-domain.com
```

### API 参考

#### 健康检查

```
GET /health
```

返回 "OK" 表示服务运行正常。

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
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "你好，请介绍一下自己。"}
  ],
  "temperature": 0.7,
  "stream": false
}
```

**响应**:

```json
{
  "id": "chat$poe-to-gpt$-123456",
  "object": "chat.completion",
  "created": 1615478285,
  "model": "GPT-4o",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！我是一个AI助手，由OpenAI开发..."
      },
      "finish_reason": "stop"
    }
  ]
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
      "id": "gpt-4o",
      "object": "model",
      "created": 1677610602,
      "owned_by": "poe"
    },
    {
      "id": "claude-3.5-sonnet",
      "object": "model",
      "created": 1677610602,
      "owned_by": "poe"
    },
    ...
  ]
}
```

### 示例请求

**使用 curl**:

```bash
curl -X POST https://your-app-name.fly.dev/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-access-token" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {"role": "user", "content": "告诉我关于量子计算的知识"}
    ],
    "temperature": 0.7
  }'
```

**使用 Python**:

```python
import requests
import json

url = "https://your-app-name.fly.dev/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-access-token"
}
data = {
    "model": "gpt-4o",
    "messages": [
        {"role": "user", "content": "告诉我关于量子计算的知识"}
    ],
    "temperature": 0.7
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())
```

**使用 JavaScript**:

```javascript
fetch("https://your-app-name.fly.dev/v1/chat/completions", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-access-token"
  },
  body: JSON.stringify({
    model: "gpt-4o",
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

## 文件结构

```
.
├── .github
│   └── workflows
│       └── deploy.yml
├── .gitignore
├── Dockerfile
├── app.py
├── config.toml (可选)
├── fly.toml
├── requirements.txt
└── README.md
```

## 自定义和扩展

### 添加新模型

当 Poe 平台添加新模型时，您可以更新 `app.py` 中的 `bot_names` 集合:

```python
bot_names = {
    "GPT-4o", "Claude-3.5-Sonnet",
    # 添加新模型名称
    "New-Model-Name",
}
```

### 修改请求流程

如果需要修改请求处理逻辑，可以编辑 `app.py` 中的 `create_completion` 函数。

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

### 重启应用

```bash
flyctl restart --app your-app-name
```

## 故障排除

### 部署失败

**问题**: GitHub Actions 部署失败
**解决方案**:

- 检查 `FLY_API_TOKEN` 是否正确设置
- 查看 GitHub Actions 日志了解详细错误信息
- 尝试手动部署并查看错误消息

### 应用运行但无法访问

**问题**: 应用已部署但无法访问
**解决方案**:

- 检查应用状态: `flyctl status --app your-app-name`
- 查看日志: `flyctl logs --app your-app-name`
- 确认应用已分配公共 IP: `flyctl ips list --app your-app-name`

### API 密钥问题

**问题**: API 返回 401 或 403 错误
**解决方案**:

- 确认环境变量已正确设置: `flyctl secrets list --app your-app-name`
- 验证请求中的访问令牌是否正确
- 检查 API 密钥是否有效: 可以通过健康检查端点验证

**问题**: 没有有效的 API 密钥
**解决方案**:

- 检查日志中的错误消息
- 使用 `flyctl secrets set POE_API_KEYS="new-key-1,new-key-2"` 更新密钥
- 重启应用: `flyctl restart --app your-app-name`

### 自定义域名问题

**问题**: 自定义域名未生效
**解决方案**:

- 确认 GitHub Variable `CUSTOM_DOMAIN` 已正确设置
- 验证 DNS 配置是否正确 (`CNAME` 记录指向 `your-app-name.fly.dev`)
- 检查 Fly.io 控制台中证书状态
- DNS 传播可能需要时间，请等待几小时后再次尝试
- 使用 `flyctl domains list` 和 `flyctl certs list` 检查状态

**问题**: SSL 证书问题
**解决方案**:

- 确保域名已正确添加: `flyctl domains add your-domain.com`
- 验证 DNS 已正确配置并已传播
- 如果需要，手动重新申请证书: `flyctl certs create your-domain.com`

## 常见问题

**Q: 可以使用多少个 API 密钥?**
A: 您可以添加任意数量的 API 密钥，系统将自动轮询使用。

**Q: 如何修改应用的区域?**
A: 编辑 `fly.toml` 文件中的 `primary_region` 设置，然后重新部署。

**Q: 应用会自动扩展吗?**
A: 是的，Fly.io 会根据流量自动扩展实例。您也可以通过 `flyctl scale` 命令手动调整。

**Q: 如何更新环境变量?**
A: 使用 `flyctl secrets set` 命令更新环境变量，例如:

```bash
flyctl secrets set POE_API_KEYS="new-key-1,new-key-2" --app your-app-name
```

**Q: 可以使用多个自定义域名吗?**
A: 是的，您可以添加多个域名。在 GitHub Variable 中用逗号分隔不同域名，例如:

```
api.example.com,chat.example.org
```

然后为每个域名添加相应的 DNS 记录。

**Q: 如何删除自定义域名?**
A: 使用以下命令移除域名:

```bash
flyctl domains remove your-domain.com --app your-app-name
```

**Q: 支持哪些模型?**
A: 支持所有 Poe 平台提供的模型，包括 GPT 系列、Claude 系列、Gemini 系列等。完整列表可通过 `/v1/models` 端点获取。

**Q: 如何停止应用?**
A: 如果您想暂时停止应用以节省资源:

```bash
flyctl scale count 0 --app your-app-name
```

---

**注意**: 使用本项目时请确保遵守 Poe API 的服务条款和使用政策。