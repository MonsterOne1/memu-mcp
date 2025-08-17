# 环境变量配置说明

本文档详细说明了 memU MCP Server 支持的所有环境变量。

## 目录

- [必需变量](#必需变量)
- [memU 配置](#memu-配置)
- [服务器配置](#服务器配置)
- [记忆管理配置](#记忆管理配置)
- [速率限制配置](#速率限制配置)
- [错误处理配置](#错误处理配置)
- [API 服务配置](#api-服务配置)
- [Render 平台配置](#render-平台配置)
- [系统配置](#系统配置)
- [配置示例](#配置示例)

## 必需变量

### MEMU_API_KEY
- **类型**: 字符串 (Secret)
- **必需**: 是
- **描述**: memU API 访问密钥
- **获取方式**: 在 [memU 平台](https://app.memu.so/api-key/) 生成
- **示例**: `memu_api_12345abcdef...`
- **安全提示**: 
  - 在 Render 中标记为 Secret
  - 不要在代码中硬编码
  - 定期轮换密钥

## memU 配置

### MEMU_BASE_URL
- **类型**: URL
- **默认值**: `https://api.memu.so`
- **描述**: memU API 服务的基础 URL
- **示例**: `https://api.memu.so`
- **注意**: 通常不需要修改，除非使用自定义部署

## 服务器配置

### MCP_SERVER_NAME
- **类型**: 字符串
- **默认值**: `memu-mcp-server`
- **Render 默认值**: `memu-mcp-server-render`
- **描述**: MCP 服务器的标识名称
- **示例**: `my-company-mcp-server`

### MCP_SERVER_VERSION
- **类型**: 字符串
- **默认值**: `0.1.0`
- **描述**: 服务器版本号
- **示例**: `1.0.0`

### LOG_LEVEL
- **类型**: 枚举
- **默认值**: `INFO`
- **可选值**: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- **描述**: 日志输出级别
- **建议**:
  - 开发环境: `DEBUG`
  - 生产环境: `INFO`
  - 问题排查: `DEBUG`

## 记忆管理配置

### DEFAULT_USER_ID
- **类型**: 字符串
- **默认值**: `default_user`
- **Render 默认值**: `render_user`
- **描述**: 未指定用户时的默认用户 ID
- **示例**: `system_user`

### DEFAULT_AGENT_ID
- **类型**: 字符串
- **默认值**: `default_agent`
- **Render 默认值**: `render_agent`
- **描述**: 未指定代理时的默认 AI 代理 ID
- **示例**: `assistant_v1`

### MAX_CONVERSATION_LENGTH
- **类型**: 整数
- **默认值**: `8000`
- **单位**: 字符数
- **描述**: 单次对话的最大字符长度
- **范围**: `1000` - `100000`
- **影响**: 
  - 过小: 可能截断长对话
  - 过大: 增加内存使用和处理时间

### MEMORY_RETENTION_DAYS
- **类型**: 整数
- **默认值**: `30`
- **单位**: 天
- **描述**: 记忆保留天数
- **示例**: `90` (保留 3 个月)

## 速率限制配置

### RATE_LIMIT_PER_MINUTE
- **类型**: 整数
- **默认值**: `60`
- **单位**: 请求数/分钟
- **描述**: 每分钟最大请求数
- **建议**: 根据 memU 计划调整

### RATE_LIMIT_PER_HOUR
- **类型**: 整数
- **默认值**: `1000`
- **单位**: 请求数/小时
- **描述**: 每小时最大请求数
- **建议**: 设置为 memU 计划限制的 80%

## 错误处理配置

### MAX_RETRY_ATTEMPTS
- **类型**: 整数
- **默认值**: `3`
- **描述**: 连接失败时的最大重试次数
- **范围**: `1` - `10`
- **影响**:
  - 过小: 可能过早放弃
  - 过大: 可能延长故障恢复时间

### WORKER_RESTART_DELAY
- **类型**: 浮点数
- **默认值**: `5`
- **单位**: 秒
- **描述**: 重试间隔的基础延迟时间
- **算法**: 指数退避 `delay * (2 ** attempt)`
- **示例**: 第一次重试 5s，第二次 10s，第三次 20s

### API_TIMEOUT
- **类型**: 整数
- **默认值**: `30`
- **单位**: 秒
- **描述**: API 请求的超时时间
- **建议**: 
  - 本地开发: `10-15` 秒
  - 生产环境: `30` 秒
  - 慢网络: `60` 秒

## API 服务配置

### API_MODE
- **类型**: 布尔值
- **默认值**: `false`
- **描述**: 是否启用 HTTP API 模式
- **用途**: Render Web Service 使用

### ENABLE_CORS
- **类型**: 布尔值
- **默认值**: `false`
- **描述**: 是否启用 CORS 支持
- **用途**: 允许跨域访问 API

### API_RATE_LIMIT
- **类型**: 整数
- **默认值**: `100`
- **单位**: 请求数/分钟
- **描述**: HTTP API 的速率限制
- **适用**: Web Service 模式

## Render 平台配置

### RENDER_DEPLOYMENT
- **类型**: 布尔值
- **默认值**: `false`
- **描述**: 标识是否在 Render 平台运行
- **作用**:
  - 切换日志格式 (JSON vs Rich)
  - 调整错误处理策略
  - 启用 Render 特定优化

### PORT
- **类型**: 整数
- **默认值**: `10000` (Render 自动设置)
- **描述**: HTTP 服务监听端口
- **注意**: 由 Render 平台自动设置，无需手动配置

## 系统配置

### PYTHONPATH
- **类型**: 路径
- **默认值**: `/app/src`
- **描述**: Python 模块搜索路径
- **Render**: 自动设置

### PYTHONUNBUFFERED
- **类型**: 布尔值
- **默认值**: `1`
- **描述**: 禁用 Python 输出缓冲
- **作用**: 确保日志实时显示

### PYTHONDONTWRITEBYTECODE
- **类型**: 布尔值
- **默认值**: `1`
- **描述**: 禁止生成 .pyc 文件
- **作用**: 减少磁盘使用

### TZ
- **类型**: 字符串
- **默认值**: `UTC`
- **描述**: 时区设置
- **建议**: 保持 UTC 以确保一致性

### LC_ALL / LANG
- **类型**: 字符串
- **默认值**: `C.UTF-8`
- **描述**: 系统语言环境设置
- **作用**: 确保 UTF-8 编码支持

## 配置示例

### 开发环境

```bash
# .env (本地开发)
MEMU_API_KEY=your_dev_api_key
LOG_LEVEL=DEBUG
DEFAULT_USER_ID=dev_user
MAX_CONVERSATION_LENGTH=5000
API_TIMEOUT=15
```

### 生产环境 (Render)

```bash
# Render Environment Variables
MEMU_API_KEY=your_prod_api_key
RENDER_DEPLOYMENT=true
LOG_LEVEL=INFO
MCP_SERVER_NAME=prod-memu-server
DEFAULT_USER_ID=prod_user
MAX_CONVERSATION_LENGTH=10000
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=2000
MAX_RETRY_ATTEMPTS=5
API_TIMEOUT=30
```

### 测试环境

```bash
# 测试环境配置
MEMU_API_KEY=your_test_api_key
LOG_LEVEL=DEBUG
DEFAULT_USER_ID=test_user
MAX_CONVERSATION_LENGTH=3000
RATE_LIMIT_PER_MINUTE=30
API_TIMEOUT=10
MAX_RETRY_ATTEMPTS=2
```

## 配置验证

### 必需变量检查

服务启动时会验证以下必需变量：

```python
required_vars = ["MEMU_API_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {missing_vars}")
    sys.exit(1)
```

### 配置健康检查

使用健康检查端点验证配置：

```bash
curl https://your-app.onrender.com/status
```

响应包含当前配置信息：

```json
{
  "configuration": {
    "memu_base_url": "https://api.memu.so",
    "log_level": "INFO",
    "max_conversation_length": 8000,
    "api_timeout": 30,
    "rate_limit_per_minute": 60
  }
}
```

## 最佳实践

### 1. 安全性
- 使用 Render Secrets 管理敏感信息
- 定期轮换 API 密钥
- 不要在日志中输出敏感信息

### 2. 性能调优
- 根据使用量调整速率限制
- 监控 API 超时并适当调整
- 优化重试策略

### 3. 监控和告警
- 设置日志级别为 INFO 或更高
- 监控健康检查端点
- 配置错误告警

### 4. 环境隔离
- 为不同环境使用不同的配置
- 避免在生产环境使用调试级别日志
- 使用环境特定的命名约定

## 故障排查

### 常见配置错误

1. **API 密钥无效**
   ```
   ERROR: Failed to initialize memU client: Authentication failed
   ```
   解决: 检查 `MEMU_API_KEY` 是否正确

2. **超时配置过小**
   ```
   WARNING: API timeout occurred
   ```
   解决: 增加 `API_TIMEOUT` 值

3. **速率限制过高**
   ```
   ERROR: Rate limit exceeded
   ```
   解决: 降低 `RATE_LIMIT_PER_MINUTE` 值

### 配置调试

启用调试日志查看配置加载过程：

```bash
LOG_LEVEL=DEBUG python -m memu_mcp_server.main
```

检查配置验证：

```bash
python -c "
from memu_mcp_server.config import Config
config = Config()
print(config.to_dict())
"
```

## 配置更新

### Render 平台更新

1. 在 Render Dashboard 中更新环境变量
2. 选择部署模式：
   - **Save and deploy**: 使用现有构建
   - **Save, rebuild, and deploy**: 重新构建应用

### 零停机更新

大多数配置更改可以通过重新部署实现零停机更新：

1. 更新环境变量
2. 触发重新部署
3. Render 自动执行滚动更新

### 配置回滚

如果配置更改导致问题：

1. 在 Render Dashboard 中回滚环境变量
2. 重新部署服务
3. 检查服务健康状态

## 支持

如需配置帮助，请：

1. 查看 [Render 部署文档](RENDER_DEPLOYMENT.md)
2. 检查 [API 文档](API.md)
3. 提交 [GitHub Issue](https://github.com/example/memu-mcp-server/issues)

记住保护好你的 API 密钥和其他敏感配置信息！