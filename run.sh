#!/bin/sh

# 检查并导入.env文件
if [ -f ".env" ]; then
    echo "Loading .env file..."
    set -a
    . ./.env
    set +a
fi

ARG1=$1

# 启动主进程
runMain(){
    # 获取环境变量WORKERS
    WORKERS=${WORKERS}
    # 判断变量是否存在
    if [ -z "$WORKERS" ]; then
        WORKERS=1
    fi
    # 启动主进程
    uvicorn app.main:app --workers ${WORKERS} --host 0.0.0.0 --port 5080
}

# 获取第一个参数，如果不存在，则执行下面的命令，如果为dev则执行另外的命令
if [ -z "$ARG1" ]; then
    runMain
elif [ "$ARG1" = "dev" ]; then
    echo "Running in development mode..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 5080
else
    echo "Unknown argument: $ARG1"
    echo "Usage: $0 [dev]"
    exit 1
fi
