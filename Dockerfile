# 使用Alpine Linux基础镜像以减小镜像大小
FROM python:3.11-alpine

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apk add --no-cache \
    # 下载工具
    aria2 \
    axel \
    # 音视频处理工具
    ffmpeg \
    # 构建依赖
    gcc \
    musl-dev \
    libffi-dev

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir .

# 创建默认下载目录
RUN mkdir -p /downloads

# 设置默认环境变量
ENV DOWNLOAD__DEFAULT_DOWNLOADER=axel
ENV DOWNLOAD__DEFAULT_QUALITY=112
ENV DOWNLOAD__DEFAULT_THREADS=16
ENV NETWORK__USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# 创建挂载点
VOLUME ["/downloads"]

# 设置默认命令
ENTRYPOINT ["bili-downloader"]
CMD ["--help"]