import os
from pathlib import Path
from typing import Any

# 版本号
VERSION = "1.0.0"

# 支持的图片格式
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "webp"}

# 最大文件大小 (默认10MB)
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))

# OCR语言 (默认中文)
OCR_LANG = os.getenv("OCR_LANG", "ch")

# OCR模型版本 (默认small，可选tiny/small)
OCR_MODEL_VERSION = os.getenv("OCR_MODEL_VERSION", "small")

# 模型目录
MODEL_DIR = Path(__file__).parent / "models"


class Config:
    """配置管理类，支持环境变量配置"""

    def __init__(self):
        self._config = {
            "token": os.getenv("TOKEN", ""),
            "workers": int(os.getenv("WORKERS", "1")),
            "max_file_size": MAX_FILE_SIZE,
            "ocr_lang": OCR_LANG,
            "ocr_model_version": OCR_MODEL_VERSION,
            "model_dir": MODEL_DIR,
        }

    def get(self, key: str, default=None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置值"""
        self._config[key] = value

    @property
    def config(self) -> dict:
        """返回配置副本"""
        return self._config.copy()


# 全局配置实例
config = Config()
