# memU MCP Server - Render 部署指南

本指南详细介绍如何在 Render 平台上部署 memU MCP Server。

## 目录

- [概述](#概述)
- [部署准备](#部署准备)
- [环境配置](#环境配置)
- [部署方法](#部署方法)
- [监控和维护](#监控和维护)
- [故障排除](#故障排除)

## 概述

### 部署架构

memU MCP Server 在 Render 上采用以下架构：

1. **Background Worker** - 运行核心 MCP 服务器 (stdio 协议)
2. **Web Service** - 提供 HTTP API 和健康检查端点

### 服务特性

- ✅ 自动扩缩容
- ✅ 零停机部署  
- ✅ 健康检查和监控
- ✅ 自动重启机制
- ✅ 结构化日志输出
- ✅ 环境变量管理

## 部署准备

### 1. 获取 memU API 密钥

1. 访问 [memU 平台](https://app.memu.so/)
2. 注册并登录账户
3. 导航到 API Keys 部分
4. 生成新的 API 密钥
5. 保存密钥以备后用

### 2. 准备代码仓库

确保你的代码已推送到 GitHub、GitLab 或 Bitbucket：

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 3. 检查依赖项

确保 `requirements.txt` 包含所有必要的依赖：

```txt
mcp>=1.0.0
memu-py>=1.0.0
aiohttp>=3.9.0
aiohttp-cors>=0.7.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
structlog>=23.2.0
rich>=13.7.0
psutil>=5.9.0
```

## 环境配置

### 必需环境变量

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `MEMU_API_KEY` | memU API 密钥 | `your_api_key_here` |

### 可选环境变量

| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| `MEMU_BASE_URL` | `https://api.memu.so` | memU API 基础 URL |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `MCP_SERVER_NAME` | `memu-mcp-server-render` | 服务器名称 |
| `DEFAULT_USER_ID` | `render_user` | 默认用户 ID |
| `DEFAULT_AGENT_ID` | `render_agent` | 默认代理 ID |
| `MAX_CONVERSATION_LENGTH` | `8000` | 最大对话长度 |
| `RATE_LIMIT_PER_MINUTE` | `60` | 每分钟请求限制 |
| `MAX_RETRY_ATTEMPTS` | `3` | 最大重试次数 |
| `WORKER_RESTART_DELAY` | `5` | 重启延迟（秒） |

## 部署方法

### 方法 1: 使用 Render Blueprint (推荐)

1. **创建 Render 账户**
   - 访问 [Render.com](https://render.com)
   - 注册并登录账户

2. **连接代码仓库**
   - 在 Render Dashboard 中点击 "New"
   - 选择 "Blueprint"
   - 连接你的 GitHub/GitLab/Bitbucket 仓库

3. **配置 Blueprint**
   - Render 会自动检测到 `render.yaml` 文件
   - 确认服务配置

4. **设置环境变量**
   - 在服务设置中找到 "Environment" 部分
   - 添加 `MEMU_API_KEY`（标记为 Secret）
   - 其他环境变量会从 Blueprint 自动配置

5. **部署**
   - 点击 "Deploy" 开始部署
   - 等待构建和部署完成

### 方法 2: 手动创建服务

#### 创建 Background Worker

1. **创建 Worker 服务**
   - 在 Render Dashboard 中点击 "New" > "Background Worker"
   - 连接你的代码仓库
   - 选择分支（通常是 `main`）

2. **配置构建设置**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m memu_mcp_server.main --render-mode`

3. **设置环境变量**
   ```
   MEMU_API_KEY=your_api_key_here (Secret)
   RENDER_DEPLOYMENT=true
   LOG_LEVEL=INFO
   ```

4. **选择计划**
   - Starter: 免费层（有限制）
   - Standard: 推荐用于生产环境

#### 创建 Web Service (可选)

1. **创建 Web 服务**
   - 在 Render Dashboard 中点击 "New" > "Web Service"
   - 连接同一个代码仓库

2. **配置构建设置**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m memu_mcp_server.api --host 0.0.0.0 --port $PORT`

3. **设置环境变量**
   ```
   MEMU_API_KEY=your_api_key_here (Secret)
   RENDER_DEPLOYMENT=true
   API_MODE=true
   ENABLE_CORS=true
   ```

## 监控和维护

### 健康检查

Web Service 提供以下监控端点：

- `GET /health` - 基础健康检查
- `GET /status` - 详细状态信息
- `GET /metrics` - 性能指标
- `GET /info` - 服务信息

### 日志查看

1. **在 Render Dashboard 中**
   - 进入服务页面
   - 点击 "Logs" 标签
   - 查看实时日志输出

2. **日志格式**
   ```
   2024-01-01 12:00:00 [INFO] memu_mcp_server: Starting memU MCP Server in Render deployment mode
   2024-01-01 12:00:01 [INFO] memu_mcp_server: memU client initialized successfully on attempt 1
   ```

### 性能监控

使用 Web Service 的监控端点：

```bash
# 检查服务状态
curl https://your-app.onrender.com/health

# 获取详细状态
curl https://your-app.onrender.com/status

# 获取性能指标
curl https://your-app.onrender.com/metrics
```

### 自动扩缩容

在 `render.yaml` 中配置：

```yaml
scaling:
  minInstances: 1
  maxInstances: 3
```

## 故障排除

### 常见问题

#### 1. 服务启动失败

**症状**: 服务无法启动，显示构建错误

**解决方案**:
- 检查 `requirements.txt` 是否包含所有依赖
- 确认 Python 版本兼容性
- 查看构建日志中的错误信息

#### 2. memU API 连接失败

**症状**: 服务启动但无法连接到 memU

**解决方案**:
- 验证 `MEMU_API_KEY` 是否正确设置
- 检查网络连接
- 确认 API 密钥有效性

#### 3. 服务频繁重启

**症状**: Background Worker 反复重启

**解决方案**:
- 检查内存使用是否超限
- 查看错误日志
- 调整重试配置
- 考虑升级到付费计划

#### 4. 健康检查失败

**症状**: 服务显示不健康状态

**解决方案**:
- 检查 `/health` 端点响应
- 验证 memU 连接状态
- 查看应用日志

### 调试技巧

#### 1. 启用调试日志

设置环境变量：
```
LOG_LEVEL=DEBUG
```

#### 2. 本地测试 Render 模式

```bash
# 模拟 Render 环境
export RENDER_DEPLOYMENT=true
export MEMU_API_KEY=your_api_key
python -m memu_mcp_server.main --render-mode
```

#### 3. 手动健康检查

```bash
# 测试 API 连接
curl -X POST https://your-app.onrender.com/test \
  -H "Content-Type: application/json" \
  -d '{"test_memu_connection": true}'
```

### 升级和迁移

#### 代码更新

1. 推送代码到仓库
2. Render 自动检测更改
3. 触发零停机部署

#### 配置更新

1. 更新环境变量
2. 选择部署模式：
   - Save and deploy: 使用现有构建
   - Save, rebuild, and deploy: 重新构建

### 成本优化

#### 免费层使用

- Background Worker: 有运行时间限制
- 服务在 15 分钟无活动后休眠
- 适合开发和测试

#### 付费层优势

- 无运行时间限制
- 更好的性能
- 专用资源
- 24/7 运行

## 进阶配置

### 自定义域名

1. 在 Web Service 设置中添加自定义域名
2. 配置 DNS 记录
3. Render 自动提供 SSL 证书

### 数据库集成

如需持久化存储：

```yaml
databases:
  - name: memu-cache
    databaseName: memu_cache
    user: memu_user
    plan: starter
```

### 多环境部署

- 开发环境: 使用免费层
- 生产环境: 使用付费计划
- 分别配置不同的环境变量

## 安全考虑

1. **API 密钥管理**
   - 使用 Render 的 Secret 功能
   - 定期轮换 API 密钥
   - 不要在代码中硬编码密钥

2. **网络安全**
   - 使用 HTTPS（Render 自动提供）
   - 配置 CORS 策略
   - 限制 API 访问

3. **日志安全**
   - 避免记录敏感信息
   - 定期清理日志文件

## 支持和资源

- [Render 官方文档](https://render.com/docs)
- [memU 官方文档](https://docs.memu.so)
- [GitHub Issues](https://github.com/example/memu-mcp-server/issues)

如需帮助，请提交 GitHub Issue 或联系支持团队。