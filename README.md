# ZOCR

基于百度PP-OCRv6模型的在线OCR识别API服务。

## 功能特性

- 支持Bearer Token认证
- 支持Docker容器化部署
- 支持常见图片格式：jpg/jpeg/png/bmp/webp
- 图片大小限制：10MB
- 返回JSON格式识别结果

## 快速开始

### Docker部署（推荐）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务（开发模式）
bash run.sh dev
```

## 配置说明

通过环境变量配置：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| TOKEN | 认证密钥 | 空（不认证） |
| WORKERS | uvicorn工作进程数 | 1 |
| OCR_LANG | OCR语言（ch/en等） | ch |
| MAX_FILE_SIZE | 最大文件大小(bytes) | 10485760 (10MB) |

## API接口

### OCR识别

```
POST /api/ocr
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数**：
- `file`: 图片文件

**响应示例**：
```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "texts": ["识别文本1", "识别文本2"],
        "scores": [0.99, 0.95],
        "boxes": [[[0,0], [100,0], [100,30], [0,30]], ...],
        "full_text": "识别文本1\n识别文本2"
    }
}
```

### 健康检查

```
GET /api/health
```

## 调用示例

```bash
# 使用curl调用
curl -X POST http://localhost:6080/api/ocr \
  -H "Authorization: Bearer your_token" \
  -F "file=@test.jpg"
```

## 端口

默认服务端口：6080
