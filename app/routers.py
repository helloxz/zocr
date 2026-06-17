from fastapi import APIRouter

from app.api.ocr import OcrHandler

ocr_handler = OcrHandler()

router = APIRouter()

# 健康检查接口
router.get("/api/health")(ocr_handler.health)

# OCR识别接口
router.post("/api/ocr")(ocr_handler.recognize)
