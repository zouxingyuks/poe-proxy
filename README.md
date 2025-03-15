# Poe API 代理

一个基于FastAPI的Poe API代理，可部署在Fly.io上。

## 特性

- 支持多个Poe API密钥轮询
- 访问令牌验证
- 兼容OpenAI格式的API接口
- 自动部署到Fly.io

## 部署步骤

### 准备工作

1. [注册Fly.io账号](https://fly.io/app/sign-up)
2. 安装Fly CLI: `curl -L https://fly.io/install.sh | sh`
3. 登录Fly.io: `flyctl auth login`

### 初始设置

1. 克隆此仓库
2. 初始化Fly.io应用:
```

flyctl launch

```
- 选择应用名称 (例如: `your-poe-proxy`)
- 选择区域 (例如: `nrt` (东京) 或 `hkg` (香港))
- 暂不部署

### 设置密钥

在Fly.io中设置环境变量:

```bash
flyctl secrets set POE_API_KEYS="your-poe-api-key-1,your-poe-api-key-2"
flyctl secrets set ACCESS_TOKENS="your-access-token-1,your-access-token-2"
```

### GitHub Actions自动部署

1. 在GitHub仓库设置中添加以下Secrets:
   - `FLY_API_TOKEN`: 使用 `flyctl auth token` 生成
2. 每次推送到main分支将自动部署

### 手动部署

```bash
flyctl deploy
```

## 使用方法

### 健康检查

```
GET https://your-app-name.fly.dev/health
```

### 聊天完成

```
POST https://your-app-name.fly.dev/v1/chat/completions

Headers:
Authorization: Bearer your-access-token

Body:
{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "temperature": 0.7
}
```

### 查询可用模型

```
GET https://your-app-name.fly.dev/v1/models

Headers:
Authorization: Bearer your-access-token
```

## 问题排查

- 查看日志: `flyctl logs`
- 检查应用状态: `flyctl status`
