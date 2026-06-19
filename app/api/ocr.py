import gzip
import io
import logging
import os
import shutil
from pathlib import Path
from typing import Optional

import numpy as np
from filelock import FileLock
from PIL import Image
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from rapidocr_onnxruntime import RapidOCR

from app.config import config
from app.utils.helper import show_json, validate_image_extension, validate_image_size

logger = logging.getLogger(__name__)

# OCR模型实例（延迟初始化）
_ocr_instance: Optional[RapidOCR] = None


def ensure_model_decompressed(model_path: str) -> str:
    """
    确保模型文件已解压
    - 如果 .onnx 存在，直接返回路径
    - 如果只有 .onnx.gz，解压后返回路径
    - 使用文件锁防止多 worker 争抢
    """
    path = Path(model_path)

    # 已解压，直接返回
    if path.exists():
        return model_path

    # 检查 .gz 文件
    gz_path = Path(model_path + ".gz")
    if not gz_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path} or {gz_path}")

    # 使用文件锁，防止多 worker 同时解压
    lock_path = model_path + ".lock"
    with FileLock(lock_path):
        # 锁内再次检查，避免重复解压
        if not path.exists():
            # 原子写入：先写临时文件，再 rename
            tmp_path = model_path + ".tmp"
            with gzip.open(gz_path, 'rb') as f_in:
                with open(tmp_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.rename(tmp_path, model_path)
            logger.info(f"Decompressed: {gz_path.name} -> {path.name}")

    return model_path


def get_ocr_instance() -> RapidOCR:
    """获取OCR单例实例"""
    global _ocr_instance
    if _ocr_instance is None:
        # 获取模型版本和路径
        model_version = config.get("ocr_model_version", "small")
        model_dir = config.get("model_dir")

        det_model_path = str(model_dir / f"ppocrv6_{model_version}" / f"ppocrv6_{model_version}_det.onnx")
        rec_model_path = str(model_dir / f"ppocrv6_{model_version}" / f"ppocrv6_{model_version}_rec.onnx")
        rec_keys_path = str(model_dir / f"ppocrv6_{model_version}_keys.txt")

        # 确保模型已解压（支持 .gz 压缩格式）
        det_model_path = ensure_model_decompressed(det_model_path)
        rec_model_path = ensure_model_decompressed(rec_model_path)

        logger.info(f"Initializing RapidOCR with model version: {model_version}")
        logger.info(f"Det model: {det_model_path}")
        logger.info(f"Rec model: {rec_model_path}")

        _ocr_instance = RapidOCR(
            det_model_path=det_model_path,
            rec_model_path=rec_model_path,
            rec_keys_path=rec_keys_path,
            intra_op_num_threads=1,
            inter_op_num_threads=1,
        )
        logger.info("RapidOCR initialized successfully")
    return _ocr_instance


class OcrHandler:
    """OCR识别接口处理类"""

    async def recognize(self, file: UploadFile = File(...)):
        """
        OCR图片识别接口
        - 支持格式：jpg/jpeg/png/bmp/webp
        - 最大大小：10MB
        """
        # 验证文件格式
        if not validate_image_extension(file.filename):
            return JSONResponse(
                status_code=400,
                content=show_json(400, f"Unsupported image format. Supported: jpg, jpeg, png, bmp, webp")
            )

        # 读取文件内容
        content = await file.read()
        file_size = len(content)

        # 验证文件大小
        if not validate_image_size(file_size):
            max_size_mb = config.get("max_file_size", 10 * 1024 * 1024) / (1024 * 1024)
            return JSONResponse(
                status_code=400,
                content=show_json(400, f"File size exceeds limit. Max size: {max_size_mb}MB")
            )

        try:
            # 获取OCR实例
            ocr = get_ocr_instance()

            # 将bytes转换为numpy数组
            image = Image.open(io.BytesIO(content))
            img_array = np.array(image)

            # 执行OCR识别
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

                    # 转换box格式为简单的坐标列表
                    box_list = [[int(point[0]), int(point[1])] for point in box]

                    texts.append(text)
                    scores.append(round(score, 4))
                    boxes.append(box_list)

            # 拼接全文
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

        except Exception as e:
            logger.error(f"OCR recognition failed: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content=show_json(500, f"OCR recognition failed: {str(e)}")
            )

    async def health(self):
        """健康检查接口"""
        return JSONResponse(
            status_code=200,
            content=show_json(200, "ok", {
                "version": config.get("version", "0.1.0"),
                "status": "running"
            })
        )
