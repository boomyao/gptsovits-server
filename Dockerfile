# 使用 NVIDIA CUDA 基础镜像
FROM nvidia/cuda:11.8.0-base-ubuntu22.04

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 设置工作目录
WORKDIR /app

# 安装 Python 和 pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app

# 安装项目依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . /app
# 复制 nltk_data
COPY ./lib/nltk_data /root/nltk_data

# 暴露端口
EXPOSE 6000

# 设置环境变量
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

# 运行应用
CMD ["python3", "app.py"]