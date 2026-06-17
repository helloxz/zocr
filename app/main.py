import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import VERSION
from app.middleware.auth import auth
from app.routers import router as my_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# 应用启动和关闭事件，上下文管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"ZOCR v{VERSION} starting...")
    # 预加载OCR模型
    from app.api.ocr import get_ocr_instance
    try:
        get_ocr_instance()
        logger.info("OCR model preloaded successfully")
    except Exception as e:
        logger.warning(f"Failed to preload OCR model: {e}")
    yield
    logger.info("ZOCR shutting down...")


app = FastAPI(
    title="ZOCR",
    description="OCR API service based on PP-OCRv6",
    version=VERSION,
    lifespan=lifespan,
)

# 添加认证中间件
app.middleware("http")(auth)

# 全局跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(my_router)


# 首页
@app.get("/")
async def index():
    return {
        "name": "ZOCR",
        "version": VERSION,
        "description": "OCR API service based on PP-OCRv6",
        "docs": "/docs"
    }
