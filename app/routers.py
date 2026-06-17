from fastapi import APIRouter

from app.api.ocr import OcrHandler
from app.api.page import PageHandler
from app.api.url_ocr import UrlOcrHandler

ocr_handler = OcrHandler()
page_handler = PageHandler()
url_ocr_handler = UrlOcrHandler()

router = APIRouter()

# 首页
router.get("/")(page_handler.index)

# 健康检查接口
router.get("/api/health")(ocr_handler.health)

# OCR识别接口（上传文件）
router.post("/api/ocr/upload")(ocr_handler.recognize)

# 通过URL进行OCR识别接口
router.get("/api/ocr/fetch")(url_ocr_handler.recognize_from_url)
