# Bilibili Bangumi Downloader

## 功能特点

- 支持下载哔哩哔哩番剧视频
- 支持多种下载器后端 (aria2, axel)
- 支持视频流合并
- 使用 `requests` 库进行网络请求
- 命令行界面 (CLI) 驱动，基于 Typer 构建
- 支持配置文件和环境变量
- 结构化的日志记录 (structlog)
- 自定义异常处理
- 模块化设计，易于扩展
- 优先下载合并：下载完一个audio和video后立即创建合并任务
- 关键字检索能力：只下载文件名包含指定关键字的剧集

## 安装

### 使用 Poetry (推荐)

```bash
# 克隆项目
git clone https://github.com/WTFGEDelphia/bili_downloader_py.git
cd bili_downloader_py

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell

# 运行程序
bili-downloader download
```

### 使用 pip

```bash
# 克隆项目
git clone https://github.com/WTFGEDelphia/bili_downloader_py.git
cd bili_downloader_py

# 创建虚拟环境 (可选但推荐)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install .

# 运行程序
bili-downloader download
```

### 使用 Docker (推荐)

```bash
# 构建镜像
docker build -t bili-downloader .
docker build -t bili-downloader:alpine .
docker build --no-cache -t bili-downloader:alpine .

# 运行交互式下载
docker run -it --rm \
  -v $(pwd)/downloads:/downloads \
  -v $(pwd)/cookie.txt:/app/cookie.txt \
  bili-downloader download

# 或者直接下载特定剧集
docker run -it --rm \
  -v $(pwd)/downloads:/downloads \
  -v $(pwd)/cookie.txt:/app/cookie.txt \
  bili-downloader download \
  --url "https://www.bilibili.com/bangumi/play/ep836727" \
  --directory "/downloads" \
  --quality 112

# 使用环境变量配置
docker run -it --rm \
  -v $(pwd)/downloads:/downloads \
  -v $(pwd)/cookie.txt:/app/cookie.txt \
  -e DOWNLOAD__DEFAULT_DOWNLOADER=aria2 \
  -e DOWNLOAD__DEFAULT_QUALITY=80 \
  bili-downloader download
```

### 使用 Docker Compose (推荐)

```bash
# 构建并启动服务
docker-compose build
docker-compose run --rm bili-downloader download

# 直接下载特定剧集
docker-compose run --rm bili-downloader download \
  --url "https://www.bilibili.com/bangumi/play/ep836727" \
  --directory "/downloads" \
  --quality 112

# 使用环境变量配置（在docker-compose.yml中修改command部分以自动下载）
# 1. 编辑 docker-compose.yml 文件，修改 command 行：
#    command: ["download", "--url", "YOUR_VIDEO_URL_HERE", "--directory", "/downloads", "--quality", "112", "--downloader", "axel"]
# 2. 运行：
#    docker-compose run --rm bili-downloader

# 使用交互式下载（需要手动输入参数）
docker-compose run --rm bili-downloader download
```

## 使用方法

### 1. 获取 Bilibili Cookie:

- 登录 Bilibili 网站
- 打开浏览器开发者工具 (F12)
- 在 Network 标签页刷新页面
- 找到任意请求，复制 Request Headers 中的 Cookie 值
- 将 Cookie 值保存到项目根目录的 `cookie.txt` 文件中

## 配置

程序支持多种配置方式，优先级从高到低为：
1. 命令行参数
2. 环境变量
3. 配置文件 (`~/.config/bili-downloader/config.toml`)
4. `.env` 文件
5. 默认值

### 配置文件

程序会在首次运行时自动创建配置文件，路径根据操作系统不同：
- **Linux/macOS**: `~/.config/bili-downloader/config.toml`
- **Windows**: `C:\Users\{username}\AppData\Roaming\bili-downloader\config.toml`

配置文件内容示例：
```toml
[download]
default_quality = 112
default_downloader = "axel"
default_threads = 16
cleanup_after_merge = false

[history]
last_url = ""
last_directory = ""

[network]
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
```

程序会自动保存上次使用的URL和下载目录到配置文件中，下次运行时会自动使用这些值作为默认值。

### 环境变量

您也可以通过环境变量来配置程序：
```bash
# 设置默认下载清晰度
export DOWNLOAD__DEFAULT_QUALITY=80

# 设置默认下载器
export DOWNLOAD__DEFAULT_DOWNLOADER=aria2

# 设置线程数
export DOWNLOAD__DEFAULT_THREADS=32

# 设置默认URL（优先级高于配置文件中的历史记录）
export DOWNLOAD__DEFAULT_URL="https://www.bilibili.com/bangumi/play/ep123"

# 设置默认下载目录（优先级高于配置文件中的历史记录）
export DOWNLOAD__DEFAULT_DIRECTORY="/path/to/downloads"

# 设置合并后是否清理原始文件
export DOWNLOAD__CLEANUP_AFTER_MERGE=true
```

环境变量优先级高于配置文件中的历史记录和默认设置，这使得您可以灵活地为不同的使用场景配置不同的默认值。

### .env 文件

复制 `.env.example` 文件为 `.env` 并根据需要修改配置：
```bash
cp .env.example .env
```

### 3. 运行下载命令:

#### 交互式下载 (推荐新手)

```bash
bili-downloader download
```

程序会交互式地提示您输入以下信息：
- 视频 URL (支持番剧主页或单集页面)
  - 默认值优先级：环境变量 `DOWNLOAD__DEFAULT_URL` > 配置文件历史记录 > 空字符串
- 下载目录
  - 默认值优先级：环境变量 `DOWNLOAD__DEFAULT_DIRECTORY` > 配置文件历史记录 > 标准下载目录 (`~/Downloads/bili_downloader`)
- 关键字过滤（可选，只下载标题包含该关键字的剧集）
  - 默认值：空字符串
- 清晰度选择
  - 默认值优先级：环境变量 `DOWNLOAD__DEFAULT_QUALITY` > 配置文件默认值
- 下载器选择 (aria2 或 axel)
  - 默认值优先级：环境变量 `DOWNLOAD__DEFAULT_DOWNLOADER` > 配置文件默认值
- 是否合并后清理原始文件
  - 默认值优先级：环境变量 `DOWNLOAD__CLEANUP_AFTER_MERGE` > 配置文件默认值

#### 命令行参数下载 (适合脚本)

```bash
bili-downloader download \\
  --url "https://www.bilibili.com/bangumi/play/ep836727" \\
  --directory "/path/to/download" \\
  --quality 112 \\
  --downloader axel \\
  --cleanup \\
  --keyword "cli"
```

#### 启用详细日志

```bash
bili-downloader download --verbose
# 或
bili-downloader download -v
```

### 4. 快速示例

创建 `cookie.txt` 文件并添加您的B站Cookie，然后运行：

```bash
# 交互式下载
bili-downloader download

# 直接下载特定剧集
bili-downloader download \\
  --url "https://www.bilibili.com/bangumi/play/ep836727" \\
  --directory "./downloads" \\
  --quality 112

# 下载标题包含"战斗"的剧集
bili-downloader download \\
  --url "https://www.bilibili.com/bangumi/play/ep836727" \\
  --directory "./downloads" \\
  --quality 112 \\
  --keyword "战斗"
```

## 支持的 URL 格式

- 番剧主页: `https://www.bilibili.com/bangumi/media/md191`
- 单集页面: `https://www.bilibili.com/bangumi/play/ep836727`

## 清晰度选项

| 代码 | 描述 |
|------|------|
| 6 | 240P 极速 (仅 MP4, 移动端 HTML5 场景) |
| 16 | 360P 流畅 (默认最低档) |
| 32 | 480P 清晰 (无需登录) |
| 64 | 720P 高清 (需登录, Web 端默认值) |
| 74 | 720P60 高帧率 (需登录) |
| 80 | 1080P 高清 (需登录, TV/APP 默认值) |
| 112 | 1080P+ 高码率 (需大会员，默认值) |
| 116 | 1080P60 高帧率 (需大会员) |
| 120 | 4K 超清 (需大会员) |
| 125 | HDR 真彩 (需大会员) |
| 126 | 杜比视界 (需大会员) |
| 127 | 8K 超高清 (需大会员) |

## 依赖

### Python 依赖
- Python 3.11+
- requests
- typer[all]
- rich
- structlog
- pydantic[dotenv]

### 外部工具依赖
- aria2c (可选，用于 aria2 下载器)
- axel (可选，用于 axel 下载器)
- ffmpeg (用于合并音视频)

确保这些工具已安装并在系统 PATH 中可用，或者将它们放在脚本目录中。

## 开发

### 代码格式化和检查

```bash
# 格式化代码
poetry run black .
poetry run isort .

# 代码检查
poetry run ruff check .

# 运行测试
poetry run pytest
```

### 目录结构

```
bili_downloader_py/
├─ .env.example         # 环境变量配置示例
├─ .gitignore
├─ CHANGELOG.md
├─ cookie.txt           # B站Cookie文件
├─ copilot-instructions.md
├─ LICENSE
├─ poetry.lock
├─ pyproject.toml
├─ QWEN.md
├─ README.md
├─ requirements-dev.txt
├─ requirements.txt
├─ bili_downloader/     # 主包
│  ├─ __init__.py
│  ├─ core/             # 纯业务逻辑
│  │  ├─ bangumi_downloader.py  # 番剧下载核心逻辑
│  │  ├─ downloader_aria2.py    # aria2 下载器实现
│  │  ├─ downloader_axel.py     # axel 下载器实现
│  │  └─ vamerger.py            # 音视频合并器
│  ├─ cli/              # Typer CLI
│  │  ├─ __init__.py
│  │  ├─ main.py        # CLI 入口点
│  │  └─ cmd_download.py # 下载命令实现
│  ├─ config/           # 配置管理
│  │  ├─ __init__.py
│  │  └─ settings.py    # 配置模型和管理
│  ├─ utils/            # 工具模块
│  │  └─ logger.py      # 日志配置
│  └─ exceptions.py     # 自定义异常
├─ docs/                # 文档
├─ examples/            # 使用示例
├─ tests/               # 测试
└─ venv/                # 虚拟环境（如果使用）
```

### 重构特性

1. **模块化 CLI**: 
   - CLI 命令已拆分为子模块，便于维护和扩展
   - 支持全局选项如 `--verbose`

2. **增强日志**:
   - 使用 structlog 实现结构化日志记录
   - 便于调试和问题追踪

3. **异常处理**:
   - 定义了自定义异常类，统一错误处理

4. **类型注解**:
   - 为核心模块添加了类型注解，提高代码可读性和维护性

5. **配置管理**:
   - 使用 Pydantic 进行配置管理，支持配置文件和环境变量

## 常见问题

### 1. 412 Precondition Failed 错误
这个错误通常是由于缺少必要的请求头造成的。程序现在会自动添加以下请求头：
- User-Agent: 模拟浏览器请求
- Referer: 设置为B站域名
- Accept: 接受所有内容类型
- Accept-Language: 支持中英文
- Accept-Encoding: 支持压缩格式

如果仍然出现此错误，请检查：
- Cookie是否有效且未过期
- 剧集是否需要大会员权限
- 网络连接是否正常

### 2. 下载失败
- 检查Cookie是否有效
- 确认网络连接正常
- 确保有足够存储空间

### 3. 合并失败
- 检查ffmpeg是否正确安装
- 确认音视频文件完整下载

### 4. 下载速度慢
- 尝试增加线程数
- 更换下载器(axel/aria2)
- 检查网络状况