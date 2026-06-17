from fastapi import Request

from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE


# 返回json信息
def show_json(code: int, msg: str, data=None):
    return {
        "code": code,
        "msg": msg,
        "data": data
    }


# 验证图片格式
def validate_image_extension(filename: str) -> bool:
    """验证图片格式是否支持"""
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_EXTENSIONS


# 验证图片大小
def validate_image_size(size: int) -> bool:
    """验证图片大小是否符合要求"""
    return 0 < size <= MAX_FILE_SIZE


# 获取客户端 IP 地址
def get_client_ip(request: Request) -> str:
    """
    获取客户端 IP 地址，处理 X-Forwarded-For 和 X-Real-IP 头的情况。
    如果 IP 地址格式不正确，则返回 "0.0.0.0"。
    """
    from ipaddress import ip_address, IPv4Address, IPv6Address

    # 尝试通过 X-Forwarded-For 获取
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        ip = xff.split(",")[0].strip()
    else:
        ip = request.headers.get("X-Real-IP")
        if ip:
            ip = ip.split(",")[0].strip()

    if not ip:
        ip = request.client.host

    try:
        parsed_ip = ip_address(ip)
        if not isinstance(parsed_ip, (IPv4Address, IPv6Address)):
            ip = "0.0.0.0"
    except ValueError:
        ip = "0.0.0.0"

    return ip
