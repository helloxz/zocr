import io
import logging
import tempfile
from typing import Optional
from urllib.parse import urlparse

import httpx
import numpy as np
from PIL import Image
from fastapi import Query
from fastapi.responses import JSONResponse

from app.api.ocr import get_ocr_instance
from app.config import config
from app.utils.helper import show_json

logger = logging.getLogger(__name__)

# 允许的MIME类型
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/bmp",
    "image/webp",
}

# MIME类型到扩展名的映射（用于Content-Type为octet-stream时的备用判断）
MIME_EXT_MAP = {
    "image/jpeg": {"jpg", "jpeg"},
    "image/png": {"png"},
    "image/bmp": {"bmp"},
    "image/webp": {"webp"},
}

# Chrome User-Agent
CHROME_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


def _validate_url(url: str) -> bool:
    """验证URL格式是否合法（必须是http/https）"""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def _extract_domain(url: str) -> str:
    """从URL中提取完整域名作为Referer"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _get_extension_from_url(url: str) -> str:
    """从URL中提取文件扩展名"""
    parsed = urlparse(url)
    path = parsed.path
    if "." in path:
        return path.rsplit(".", 1)[-1].lower()
    return ""


def _check_content_type(content_type: str, url: str) -> bool:
    """检查Content-Type是否为合法的图片类型"""
    if not content_type:
        # 没有Content-Type，通过扩展名判断
        ext = _get_extension_from_url(url)
        for mime, exts in MIME_EXT_MAP.items():
            if ext in exts:
                return True
        return False

    # 提取主类型（去掉charset等参数）
    mime = content_type.split(";")[0].strip().lower()

    if mime in ALLOWED_MIME_TYPES:
        return True

    # application/octet-stream 或其他未知类型，通过扩展名判断
    if mime == "application/octet-stream" or mime not in ALLOWED_MIME_TYPES:
        ext = _get_extension_from_url(url)
        for allowed_mime, exts in MIME_EXT_MAP.items():
            if ext in exts:
                return True

    return False


class UrlOcrHandler:
    """通过URL进行OCR识别的处理类"""

    async def recognize_from_url(self, url: str = Query(..., description="Image URL to recognize")):
        """
        通过图片URL进行OCR识别
        """
        # 1. 验证URL格式
        if not _validate_url(url):
            return JSONResponse(
                status_code=400,
                content=show_json(-1000, "Invalid URL format. Must be http or https")
            )

        referer = _extract_domain(url)

        try:
            # 2. 使用GET请求获取headers（stream模式不下载body）
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(connect=10, read=30, write=10, pool=10),
                follow_redirects=True,
                headers={
                    "User-Agent": CHROME_UA,
                    "Referer": referer,
                }
            ) as client:
                async with client.stream("GET", url) as response:
                    # 检查HTTP状态码
                    if response.status_code != 200:
                        return JSONResponse(
                            status_code=400,
                            content=show_json(-1000, f"Failed to fetch image. HTTP status: {response.status_code}")
                        )

                    # 3. 检查Content-Length
                    content_length = response.headers.get("content-length")
                    if not content_length:
                        return JSONResponse(
                            status_code=400,
                            content=show_json(-1000, "Missing Content-Length header. Cannot determine file size")
                        )

                    try:
                        file_size = int(content_length)
                    except ValueError:
                        return JSONResponse(
                            status_code=400,
                            content=show_json(-1000, "Invalid Content-Length header")
                        )

                    # 检查文件大小
                    max_size = config.get("max_file_size", 10 * 1024 * 1024)
                    if file_size <= 0 or file_size > max_size:
                        max_size_mb = max_size / (1024 * 1024)
                        return JSONResponse(
                            status_code=400,
                            content=show_json(-1000, f"File size exceeds limit. Max size: {max_size_mb}MB")
                        )

                    # 4. 检查MIME类型
                    content_type = response.headers.get("content-type", "")
                    if not _check_content_type(content_type, url):
                        return JSONResponse(
                            status_code=400,
                            content=show_json(-1000, "Unsupported image format. Supported: jpg, jpeg, png, bmp, webp")
                        )

                    # 5. 下载图片到临时文件
                    with tempfile.NamedTemporaryFile(delete=True, suffix=".tmp") as tmp_file:
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            tmp_file.write(chunk)
                        tmp_file.flush()

                        # 读取临时文件内容
                        tmp_file.seek(0)
                        content = tmp_file.read()

            # 6. 调用OCR识别
            ocr = get_ocr_instance()
            image = Image.open(io.BytesIO(content))
            img_array = np.array(image)

            result, _ = ocr(img_array)

            # 解析结果
            texts = []
            scores = []
            boxes = []

            if result:
                for line in result:
                    box = line[0]
                    text = line[1]
                    score = line[2]

                    box_list = [[int(point[0]), int(point[1])] for point in box]

                    texts.append(text)
                    scores.append(round(score, 4))
                    boxes.append(box_list)

            full_text = "\n".join(texts)

            return JSONResponse(
                status_code=200,
                content=show_json(200, "success", {
                    "texts": texts,
                    "scores": scores,
                    "boxes": boxes,
                    "full_text": full_text
                })
            )

        except httpx.TimeoutException:
            return JSONResponse(
                status_code=400,
                content=show_json(-1000, "Download timeout. Image download exceeded 30 seconds")
            )
        except httpx.RequestError as e:
            return JSONResponse(
                status_code=400,
                content=show_json(-1000, f"Network error: {str(e)}")
            )
        except Exception as e:
            logger.error(f"URL OCR failed: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content=show_json(-1000, f"OCR recognition failed: {str(e)}")
            )
