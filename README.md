# Poe Proxy API

一个将Poe API代理转换为OpenAI兼容格式的服务，完全托管在Cloudflare Workers上。通过此服务，您可以使用OpenAI兼容的客户端调用多种AI模型，包括GPT-4o、Claude-3.5-Sonnet、Gemini、Llama等。

## ✨ 功能特点

- 🔄 将Poe API请求转换为OpenAI兼容的格式
- 🤖 支持多种AI模型，包括最新的Claude、GPT、Gemini等
- 🌐 完全托管在Cloudflare上，无需服务器
- 🔑 支持多个API密钥轮询使用
- 🔒 内置访问令牌认证系统
- 📊 流式响应支持
- 📋 OpenAI兼容的接口格式，适用于大多数AI客户端

## 📋 支持的模型

支持众多AI模型，包括但不限于：

- GPT系列: GPT-4o, GPT-4o-mini等
- Claude系列: Claude-3.5-Sonnet, Claude-3-opus等
- Gemini系列: Gemini-1.5-Pro, Gemini-1.5-Flash等
- Llama系列: Llama-3.1-405B, Llama-3.1-70B等
- 其他: o1, Qwen, DALL-E-3, StableDiffusionXL等

## 🚀 部署指南

### 前置条件

1. GitHub账号
2. Cloudflare账号
3. Poe账号及API密钥

### 部署步骤

1. **Fork或克隆此仓库**
   
   点击仓库右上角的"Fork"按钮或克隆到本地后推送到您自己的GitHub仓库。

2. **设置GitHub Secrets**
   
   在仓库的"Settings > Secrets and variables > Actions"中添加以下secrets:
   
   - `CF_API_TOKEN`: Cloudflare API令牌
   - `CF_ACCOUNT_ID`: Cloudflare账户ID
   - `POE_APIKEYS`: Poe API密钥，多个密钥用逗号分隔
   - `API_ACCESS_TOKENS`: 访问令牌，多个令牌用逗号分隔

3. **自定义域名（可选）**
   
   在`wrangler.toml`文件中修改`routes`部分，使用您自己的域名：
   
   ```toml
   [env.production]
   routes = [
     { pattern = "api.your-domain.com/*", zone_name = "your-domain.com" }
   ]
   ```

4. **触发部署**
   
   - 推送代码到main分支，或
   - 在GitHub仓库的"Actions"标签页中手动触发工作流

5. **验证部署**
   
   部署完成后，可通过健康检查端点进行验证：
   ```
   curl https://api.your-domain.com/health
   ```

## ⚙️ 配置说明

### 环境变量

- `POE_APIKEYS`: Poe API密钥列表，以逗号分隔
- `API_ACCESS_TOKENS`: 访问令牌列表，以逗号分隔
- `PORT`: 应用端口，默认为8080

### config.toml

可以通过`config.toml`配置如下选项：

```toml
port = 8080
apikey = []
accessTokens = []
timeout = 120
```

## 📝 使用方法

### 接口格式

服务提供兼容OpenAI的接口：

```
POST /v1/chat/completions
POST /chat/completions
```

### 请求示例

```bash
curl -X POST "https://api.your-domain.com/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "model": "claude-3.5-sonnet",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "stream": true,
    "temperature": 0.7
  }'
```

### 客户端整合

此API与所有支持OpenAI API的客户端兼容，只需更改API基础URL即可。

## 🔒 安全注意事项

- 请勿在公共代码中硬编码API密钥或访问令牌
- 定期轮换访问令牌
- 使用GitHub Secrets存储敏感信息
- 限制API的访问范围和使用率

## 🛠 故障排除

### 常见问题

1. **部署失败**
   - 检查Cloudflare API令牌权限
   - 确认GitHub Actions日志获取详细错误信息

2. **认证错误**
   - 验证访问令牌配置是否正确
   - 确认请求中Bearer令牌格式正确

3. **API调用失败**
   - 确保Poe API密钥有效
   - 检查模型名称拼写是否正确

## 🤝 贡献指南

欢迎通过以下方式贡献：

1. 提交Issues报告问题或建议功能
2. 提交Pull Requests改进代码
3. 更新文档或添加示例

## 📄 许可证

MIT License

## 免责声明

本项目仅供学习和研究使用。使用时请遵守相关服务的使用条款和API限制。

---

**注意**: 在使用此服务时，请确保遵守Poe的服务条款和API使用政策。