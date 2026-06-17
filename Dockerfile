FROM python:3.11-slim

# 设置工作目录
WORKDIR /opt/zocr

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    libxcb1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 创建并激活虚拟环境，然后安装依赖
COPY requirements.txt .
RUN python -m venv myenv && \
    . myenv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# 复制所有项目文件
COPY . .

# 暴露端口
EXPOSE 5080

# 启动命令
CMD ["bash", "run.sh"]
