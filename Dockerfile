# --------------------------------------
# ① 构建阶段：仅生成 wheel
# --------------------------------------
FROM python:3.11-slim AS builder

# 换国内软件源 & 安装一次性编译工具
ARG DEBIAN_FRONTEND=noninteractive
RUN set -e && \
    sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g' \
        /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential libffi-dev && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

WORKDIR /src

# 拷贝项目元数据 & 源码
COPY pyproject.toml README.md ./
COPY bili_downloader ./bili_downloader

# 安装 Poetry → 禁用虚拟环境 → 生成 wheel
RUN pip install --no-cache-dir poetry -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    poetry config virtualenvs.create false && \
    poetry build --format=wheel && \
    ls -1 dist/*.whl

# --------------------------------------
# ② 运行阶段：极致精简
# --------------------------------------
FROM python:3.11-slim

# 换源 & 安装「最小所需软件堆」
ARG DEBIAN_FRONTEND=noninteractive
RUN set -e && \
    sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g' \
        /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        aria2 axel ffmpeg && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
           /usr/share/doc/* /usr/share/man/* /usr/share/info/*

# 非 root 用户
RUN groupadd -r bili && useradd -r -g bili bili

WORKDIR /app

# wheel 安装 & 路径检查
COPY --from=builder /src/dist/*.whl ./
RUN pip --no-cache-dir install *.whl && \
    rm -f *.whl && \
    which bili-downloader

# 将业务代码放置镜像（方便热更新）
COPY --chown=bili:bili bili_downloader ./bili_downloader

# 创建下载目录并赋权
RUN install -d -o bili -g bili /downloads

# 默认环境变量
ENV DOWNLOAD__DEFAULT_DOWNLOADER=axel \
    DOWNLOAD__DEFAULT_QUALITY=112 \
    DOWNLOAD__DEFAULT_THREADS=16 \
    NETWORK__USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

VOLUME ["/downloads"]

# 切换到非root用户
USER bili

# 检查脚本是否出现
RUN which bili-downloader || (echo "CLI binary not found" && exit 1)

ENTRYPOINT ["bili-downloader"]
CMD ["--help"]