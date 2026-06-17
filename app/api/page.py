import os

from fastapi.responses import HTMLResponse

# 静态文件目录路径
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")


class PageHandler:
    """Web页面处理类"""

    async def index(self):
        """返回首页HTML"""
        html_path = os.path.join(STATIC_DIR, "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
