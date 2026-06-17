FROM python:3.11-slim

# 设置工作目录
WORKDIR /opt/zocr

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app ./app
COPY run.sh .

# 暴露端口
EXPOSE 6080

# 启动命令
CMD ["bash", "run.sh"]
