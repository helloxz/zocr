[English](README.md) | [中文](README_zh.md)

# ZOCR

Online OCR recognition API service based on Baidu PP-OCRv6 model.

![CleanShot 2026-06-18 at 08.36.40@2x.png](https://img.rss.ink/2026/06/18/PyUM5Mjm.png)

## Features

- Supports Bearer Token authentication
- Supports Docker containerized deployment
- Supports common image formats: jpg/jpeg/png/bmp/webp
- Image size limit: 10MB
- Returns JSON format recognition results

## Quick Start

### Docker Compose Deployment (Recommended)

Create a `compose.yaml` file:

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

Optional environment variables:
- `ZOCR_WORKERS`: Number of uvicorn worker processes, default 1
- `ZOCR_MODEL_VERSION`: OCR model version (tiny/small), default small
- `ZOCR_MAX_FILE_SIZE`: Maximum file size (bytes), default 10485760

Start the service:

```bash
# Start the service
docker compose up -d
```

### Local Development

Environment requirements: Python >= 3.11

```bash
# Install dependencies
pip install -r requirements.txt

# Start the service (development mode)
bash run.sh dev
```

## Configuration

Configure via environment variables. If ZOCR_TOKEN is empty, authentication is skipped:

| Variable | Description | Default |
|----------|-------------|---------|
| ZOCR_TOKEN | Authentication key | Empty (no auth) |
| ZOCR_WORKERS | Number of uvicorn worker processes | 1 |
| ZOCR_MODEL_VERSION | OCR model version (tiny/small) | small |
| ZOCR_MAX_FILE_SIZE | Maximum file size (bytes) | 10485760 (10MB) |

## API Endpoints

### OCR Recognition (Upload File)

```
POST /api/ocr/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**Request Parameters**:
- `file`: Image file

### OCR Recognition (Via URL)

```
GET /api/ocr/fetch?url=<image_url>
Authorization: Bearer <token>
```

**Request Parameters**:
- `url`: Image URL address

### Response Example

```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "texts": ["Recognized text 1", "Recognized text 2"],
        "scores": [0.99, 0.95],
        "boxes": [[[0,0], [100,0], [100,30], [0,30]], ...],
        "full_text": "Recognized text 1\nRecognized text 2"
    }
}
```

### Health Check

```
GET /api/health
```

## Usage Examples

```bash
# Using curl (upload file)
curl -X POST http://localhost:5080/api/ocr/upload \
  -H "Authorization: Bearer your_token" \
  -F "file=@test.jpg"

# Using curl (via URL)
curl "http://localhost:5080/api/ocr/fetch?url=https://example.com/image.jpg" \
  -H "Authorization: Bearer your_token"
```

## Contact

- X: [@xiaozblog](https://x.com/xiaozblog)