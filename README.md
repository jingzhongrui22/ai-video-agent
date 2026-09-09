# AI 文本转视频智能体

基于 Python 3.12 和 FastAPI 的后端基础项目，目前仅提供健康检查接口。
尚未实现 DeepSeek、TTS、数字人或工作流，也未引入 LangChain、LangGraph、Redis 或数据库。

## 项目结构

```text
app/
  __init__.py
  main.py           # 应用入口和健康检查
  api/              # API 路由预留
  services/         # 业务服务预留
  schemas/          # 数据模型预留
  core/             # 配置和公共组件预留
tests/
  test_health.py
storage/
  audio/
  video/
  subtitle/
  output/
.env.example
.gitignore
requirements.txt
README.md
```

## 环境准备

在项目根目录使用 PowerShell。需要已安装 Python 3.12。
如果项目尚无 `.venv`，先创建项目内虚拟环境：

```powershell
py -3.12 -m venv .venv
```

将依赖安装到项目虚拟环境：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

无需激活虚拟环境或修改系统执行策略。依赖版本与本项目验证环境一致。
Pydantic、httpx 和 python-dotenv 作为基础依赖预留；当前无外部 API 调用。

## 启动

在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

`--reload` 用于本地开发。访问 `http://127.0.0.1:8000/health`，返回 HTTP 200：

```json
{
  "status": "ok",
  "service": "ai-video-agent"
}
```

交互式 API 文档地址：`http://127.0.0.1:8000/docs`。

## 测试

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

测试通过进程内客户端验证响应状态码与完整 JSON，无需启动服务器，也不访问外部 API。

## 配置与存储

当前无需 API Key 或 `.env` 文件，应用尚未加载环境变量配置。
后续需要配置时，可复制 `.env.example` 为 `.env`，真实密钥只放在本地配置中，禁止硬编码或提交。
`.gitignore` 已忽略 `.env`、虚拟环境、缓存以及 `storage/` 中生成的文件，并保留目录占位文件。
