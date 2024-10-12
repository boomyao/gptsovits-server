# 使用适用于 arm64 架构的基础镜像
FROM arm64v8/python:3.10-slim

# 设置环境变量，防止交互式界面影响构建
ENV DEBIAN_FRONTEND=noninteractive

# 替换源列表
RUN rm -f /etc/apt/sources.list && \
    echo "deb [arch=arm64] http://mirrors.aliyun.com/debian/ bookworm main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb [arch=arm64] http://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb [arch=arm64] http://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb [arch=arm64] http://mirrors.aliyun.com/debian/ bookworm-backports main contrib non-free" >> /etc/apt/sources.list

# 更新软件包列表并安装依赖
RUN apt-get update && \
    apt-get install -y libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app

# 安装项目依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . /app

RUN python3 gptsovits_manager.py

# 暴露端口
EXPOSE 6000

# 设置环境变量
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

# 运行应用
CMD ["python3", "app.py"]