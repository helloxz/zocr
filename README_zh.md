[English](README.md) | [中文](README_zh.md)

# ZOCR

基于百度PP-OCRv6模型的在线OCR识别API服务。

![CleanShot 2026-06-18 at 08.36.40@2x.png](https://img.rss.ink/2026/06/18/PyUM5Mjm.png)

## 功能特性

- 支持Bearer Token认证
- 支持Docker容器化部署
- 支持常见图片格式：jpg/jpeg/png/bmp/webp
- 图片大小限制：10MB
- 返回JSON格式识别结果

## 快速开始

### Docker Compose部署（推荐）

创建`compose.yaml`文件：

```yaml
services:
  zocr:
    image: helloz/zocr
    container_name: zocr
    ports:
      - "5080:5080"
    environment:
      - ZOCR_TOKEN=your_token_here
    restart: always
```

可选环境变量：
- `ZOCR_WORKERS`: uvicorn工作进程数，默认1
- `ZOCR_MODEL_VERSION`: OCR模型版本（tiny/small），默认small
- `ZOCR_MAX_FILE_SIZE`: 最大文件大小(bytes)，默认10485760

启动服务：

```bash
# 启动服务
docker compose up -d
```

### 本地开发

环境要求：Python >= 3.11

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务（开发模式）
bash run.sh dev
```

## 配置说明

通过环境变量配置，ZOCR_TOKEN为空则跳过认证：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| ZOCR_TOKEN | 认证密钥 | 空（不认证） |
| ZOCR_WORKERS | uvicorn工作进程数 | 1 |
| ZOCR_MODEL_VERSION | OCR模型版本（tiny/small） | small |
| ZOCR_MAX_FILE_SIZE | 最大文件大小(bytes) | 10485760 (10MB) |

## API接口

### OCR识别（上传文件）

```
POST /api/ocr/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数**：
- `file`: 图片文件

### OCR识别（通过URL）

```
GET /api/ocr/fetch?url=<image_url>
Authorization: Bearer <token>
```

**请求参数**：
- `url`: 图片URL地址

### 响应示例

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
# 使用curl调用（上传文件）
curl -X POST http://localhost:5080/api/ocr/upload \
  -H "Authorization: Bearer your_token" \
  -F "file=@test.jpg"

# 使用curl调用（通过URL）
curl "http://localhost:5080/api/ocr/fetch?url=https://example.com/image.jpg" \
  -H "Authorization: Bearer your_token"
```

## 联系我

- X：[@xiaozblog](https://x.com/xiaozblog)

## 其它产品

* ZMark书签管理：[https://www.zmark.app/](https://www.zmark.app/)
* Zdir文件管理：[https://www.zdir.pro/](https://www.zdir.pro/)
* Zurl短链接服务：[@helloxz/zurl](https://github.com/helloxz/zurl)
* Znsfw图片鉴黄：[@helloxz/znsfw](https://github.com/helloxz/znsfw)