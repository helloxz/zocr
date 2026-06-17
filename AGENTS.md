# ZOCR 开发指南

## 项目概述

基于百度PP-OCRv6的OCR API服务，FastAPI + Uvicorn + RapidOCR。

## 关键入口

- `app/main.py` - FastAPI应用入口
- `app/routers.py` - 路由定义（`/api/ocr/upload`, `/api/ocr/fetch`, `/api/health`）
- `app/api/ocr.py` - OCR核心逻辑（延迟初始化单例）
- `app/middleware/auth.py` - Bearer Token认证（TOKEN为空则跳过）
- `app/config.py` - 环境变量配置

## 开发命令

```bash
# 本地开发（热重载，端口5080）
bash run.sh dev

# 生产模式
bash run.sh

# Docker部署
docker-compose build && docker-compose up -d
```

## 端口映射陷阱

- Docker对外端口：`6080`
- 容器内uvicorn端口：`5080`
- 映射关系：`6080:5080`
- 调试时注意：curl测试用6080，日志显示5080

## 模型配置

两个变体，通过`OCR_MODEL_VERSION`环境变量切换：
- `tiny` - 快速，精度较低
- `small` - 准确，推荐（默认）

模型文件位置：`app/models/ppocrv6_{variant}/`

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TOKEN` | 认证密钥 | 空（无认证） |
| `WORKERS` | uvicorn进程数 | 1 |
| `OCR_MODEL_VERSION` | 模型版本 | small |
| `MAX_FILE_SIZE` | 最大文件(bytes) | 10485760 |

配置文件：`.env`（不提交git）

## 注意事项

- 无测试框架，无lint/typecheck配置
- OCR实例懒加载，首次请求会初始化模型
- 认证中间件排除：`/`, `/docs*`, `/api/health`
