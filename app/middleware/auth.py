from fastapi import Request
from typing import Callable
from fastapi.responses import JSONResponse

from app.utils.helper import show_json


# Bearer Token认证中间件
async def auth(request: Request, call_next: Callable):
    # 获取路由路径
    path = request.url.path
    # 首页、文档和健康检查接口，不需要鉴权
    if path == "/" or path.startswith("/docs") or path == "/api/health":
        return await call_next(request)

    # 从环境变量中获取TOKEN
    import os
    os_token = os.getenv("TOKEN", "")

    # 如果没获取到，则不进行鉴权，直接放行
    if not os_token:
        return await call_next(request)

    # 获取请求头中的token
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse(
            status_code=401,
            content=show_json(401, "Token invalid")
        )

    # token的格式是Bearer xxx
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return JSONResponse(
            status_code=401,
            content=show_json(401, "Token invalid")
        )

    # 从header中获取的token
    header_token = parts[1]
    # 与环境变量中的token对比
    if header_token != os_token:
        return JSONResponse(
            status_code=401,
            content=show_json(401, "Token invalid")
        )

    # 鉴权通过，放行
    response = await call_next(request)
    return response
