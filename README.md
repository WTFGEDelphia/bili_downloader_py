# 哔哩哔哩番剧下载器

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/dependency%20manager-Poetry-blue)](https://python-poetry.org/)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-blue)

一个功能强大且用户友好的命令行工具，用于下载哔哩哔哩番剧视频，支持高质量和高效率。

## 🌟 功能特点

- **高画质下载**：支持多种视频画质，包括 1080P+、4K、HDR 和杜比视界（需要哔哩哔哩大会员）。
- **灵活的下载器**：可在 `aria2` 和 `axel` 之间选择，以优化下载速度。
- **智能合并**：自动将下载的音频和视频流合并成单个 `.mkv` 文件。
- **关键词过滤**：仅下载标题包含特定关键词的剧集。
- **可配置且持久化**：使用 TOML 配置文件和环境变量保存您的偏好设置和历史记录。
- **Docker 支持**：在隔离的容器环境中运行下载器，便于设置和部署。
- **详细日志**：使用 `structlog` 进行结构化日志记录，便于调试和监控。
- **模块化设计**：易于扩展和维护，采用 Python 最佳实践构建。

## 📦 安装

### 先决条件

在安装哔哩哔哩番剧下载器之前，请确保您的系统上已安装以下软件：

- **Python 3.11 或更高版本** ([下载 Python](https://www.python.org/downloads/))
- **Poetry**（推荐用于依赖管理） - [安装指南](https://python-poetry.org/docs/#installation)
- **FFmpeg**（用于合并音视频） - [下载 FFmpeg](https://ffmpeg.org/download.html)
- **Aria2 或 Axel**（可选，用于加速下载） - 通过系统的包管理器安装或从其官方网站下载。

### 方式一：使用 Poetry（推荐）

```bash
# 克隆仓库
git clone https://github.com/WTFGEDelphia/bili_downloader_py.git
cd bili_downloader_py

# 安装依赖
poetry install

# 运行程序
poetry run  bili-downloader download
```

### 方式二：使用 pip

```bash
# 克隆仓库
git clone https://github.com/WTFGEDelphia/bili_downloader_py.git
cd bili_downloader_py

# （可选但推荐）创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或者
.venv\Scripts\activate     # Windows

# 安装包
pip install .

# 运行程序
bili-downloader download
```

### 方式三：使用 Docker（推荐用于隔离）

```bash
# 构建 Docker 镜像
docker build --no-cache -t bili-downloader .

# 交互式运行
docker run -it --rm \\
  -v $(pwd)/downloads:/app/downloads \\
  -v $(pwd)/cookie.txt:/app/cookie.txt:ro \\
  bili-downloader download

# 或者直接下载特定剧集
docker run -it --rm \\
  -v $(pwd)/downloads:/app/downloads \\
  -v $(pwd)/cookie.txt:/app/cookie.txt:ro \\
  bili-downloader download \\
  --url "https://www.bilibili.com/bangumi/play/ep836727" \\
  --directory "/app/downloads" \\
  --quality 112

# 使用环境变量进行配置
docker run -it --rm \\
  -v $(pwd)/downloads:/app/downloads \\
  -v $(pwd)/cookie.txt:/app/cookie.txt:ro \\
  -e DOWNLOAD__DEFAULT_DOWNLOADER=aria2 \\
  -e DOWNLOAD__DEFAULT_QUALITY=80 \\
  bili-downloader download
```

### 方式四：使用 Docker Compose（推荐用于易用性）

```bash
# 构建并交互式运行
docker-compose run --rm bili-downloader download

# 直接下载特定剧集
docker-compose run --rm bili-downloader download \\
  --url "https://www.bilibili.com/bangumi/play/ep836727" \\
  --directory "/app/downloads" \\
  --quality 112

# 编辑 `docker-compose.yml` 以设置默认命令来自动下载
# 1. 修改 `docker-compose.yml` 中的 `command` 行：
#    command: ["download", "--url", "YOUR_VIDEO_URL_HERE", "--directory", "/app/downloads", "--quality", "112", "--downloader", "axel"]
# 2. 运行：
#    docker-compose run --rm bili-downloader
```

## 🚀 快速开始

### 1. 获取您的哔哩哔哩 Cookie

要下载视频，您需要一个有效的哔哩哔哩账户 Cookie。您可以通过以下方式获取：

#### 方法一：使用 QR 码登录（推荐）

使用内置的 QR 码登录功能，通过手机 Bilibili App 扫码登录：

```bash
# 使用 QR 码登录（默认方法）
bili-downloader login

# 指定输出文件
bili-downloader login --output ./my_cookie.txt

# 设置超时时间（秒）
bili-downloader login --timeout 300
```

程序将生成一个可以直接在终端中显示的 QR 码，您可以用手机 Bilibili App 扫描该 QR 码并确认登录。登录成功后，Cookie 将自动保存到指定文件中。

#### 方法二：使用浏览器登录

使用内置的浏览器登录功能，在默认浏览器中打开 Bilibili 登录页面：

```bash
# 使用浏览器登录
bili-downloader login --method web

# 指定输出文件
bili-downloader login --method web --output ./my_cookie.txt
```

程序将打开默认浏览器并引导您完成登录流程，然后提供详细的说明帮助您手动提取 Cookie。

#### 方法三：手动获取 Cookie

1. 登录 [哔哩哔哩](https://www.bilibili.com/)。
2. 打开浏览器的开发者工具 (F12)。
3. 转到 Network 标签页并刷新页面。
4. 找到任意请求，右键单击并选择 "Copy" > "Copy Request Headers"。
5. 从复制的头部信息中提取 `Cookie` 值。
6. 将此 Cookie 值保存到项目根目录下名为 `cookie.txt` 的文件中。

### 2. 运行下载器

#### 登录获取 Cookie（推荐使用 QR 码登录）

```bash
# 使用 QR 码登录（默认方法）
bili-downloader login

# 使用 QR 码登录并指定输出文件
bili-downloader login --output ./my_cookie.txt

# 使用 QR 码登录并设置超时时间（秒）
bili-downloader login --timeout 300

# 使用浏览器登录
bili-downloader login --method web

# 使用浏览器登录并指定输出文件
bili-downloader login --method web --output ./my_cookie.txt
```

#### 交互模式（推荐给初学者）

```bash
bili-downloader download
```

程序将提示您输入：
- 视频 URL（番剧主页或剧集页面）
- 下载目录
- 关键词过滤器（可选）
- 视频画质
- 下载器 (aria2 或 axel)
- 合并后是否清理原始文件

#### 命令行模式（用于脚本/自动化）

```bash
bili-downloader download \\
  --url "https://www.bilibili.com/bangumi/play/ep836727" \\
  --directory "./downloads" \\
  --quality 112 \\
  --downloader axel \\
  --cleanup \\
  --keyword "cli"
```

#### 启用详细日志

```bash
bili-downloader download --verbose
# 或者
bili-downloader download -v
```

### 3. 快速示例

创建 `cookie.txt` 文件后，您可以运行：

```bash
# 通过 QR 码登录（推荐）
bili-downloader login

# 通过浏览器登录
bili-downloader login --method web

# 通过 QR 码登录并指定输出文件
bili-downloader login --output ./my_cookie.txt

# 交互式下载
bili-downloader download

# 下载特定剧集
bili-downloader download \\
  --url "https://www.bilibili.com/bangumi/play/ep836727" \\
  --directory "./downloads" \\
  --quality 112

# 仅下载标题中包含"战斗"的剧集
bili-downloader download \\
  --url "https://www.bilibili.com/bangumi/play/ep836727" \\
  --directory "./downloads" \\
  --quality 112 \\
  --keyword "战斗"

## 📚 支持的 URL 格式

- **番剧主页**：`https://www.bilibili.com/bangumi/media/md191`
- **剧集页面**：`https://www.bilibili.com/bangumi/play/ep836727`

## 📺 视频画质选项

| 代码 | 描述                           |
|------|--------------------------------|
| 6    | 240P 极速 (仅限 MP4)           |
| 16   | 360P 流畅 (默认最低档)         |
| 32   | 480P 清晰 (无需登录)           |
| 64   | 720P 高清 (需登录)             |
| 74   | 720P60 高帧率 (需登录)         |
| 80   | 1080P 高清 (需登录)            |
| 112  | 1080P+ 高码率 (需大会员)       |
| 116  | 1080P60 高帧率 (需大会员)      |
| 120  | 4K 超清 (需大会员)             |
| 125  | HDR 真彩 (需大会员)            |
| 126  | 杜比视界 (需大会员)            |
| 127  | 8K 超高清 (需大会员)           |

## ⚙️ 配置

下载器支持通过多种方式进行配置，优先级如下（从高到低）：

1. 命令行参数
2. 环境变量
3. 配置文件 (`~/.config/bili-downloader/config.toml`)
4. `.env` 文件
5. 内置默认值

### 配置文件

首次运行时，程序将创建一个默认配置文件：
- **Linux/macOS**：`~/.config/bili-downloader/config.toml`
- **Windows**：`C:\\Users\\{username}\\AppData\\Roaming\\bili-downloader\\config.toml`

示例 `config.toml`：

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

程序将自动保存上次使用的 URL 和下载目录，这些将在后续运行中用作默认值。

### 环境变量

您也可以使用环境变量来配置程序：

```bash
# 设置默认下载画质
export DOWNLOAD__DEFAULT_QUALITY=80

# 设置默认下载器
export DOWNLOAD__DEFAULT_DOWNLOADER=aria2

# 设置线程数
export DOWNLOAD__DEFAULT_THREADS=32

# 设置默认 URL（覆盖历史记录）
export DOWNLOAD__DEFAULT_URL="https://www.bilibili.com/bangumi/play/ep123"

# 设置默认目录（覆盖历史记录）
export DOWNLOAD__DEFAULT_DIRECTORY="/path/to/downloads"

# 设置合并后是否清理
export DOWNLOAD__CLEANUP_AFTER_MERGE=true
```

环境变量的优先级高于配置文件中的历史记录和默认设置。

### .env 文件

将 `.env.example` 文件复制为 `.env` 并根据需要进行修改：

```bash
cp .env.example .env
```

### 🛠️ 依赖

#### Python 依赖

- Python 3.11+
- requests
- typer[all]
- rich
- structlog
- pydantic[dotenv]
- pydantic-settings
- toml
- qrcode[pil] (用于生成二维码)

#### 外部工具

- **FFmpeg**：合并音视频流所必需。
- **Aria2**（可选）：使用 `aria2` 下载器进行加速下载。
- **Axel**（可选）：使用 `axel` 下载器进行加速下载。

确保这些工具已安装并且在您的系统 PATH 中可用，或将它们放在脚本目录中。

## 🧪 开发

### 代码格式化和检查

```bash
# 格式化代码
poetry run black .
poetry run isort .

# 检查代码
poetry run ruff check .

# 运行测试
poetry run pytest
```

### CLI 命令

该工具提供以下命令：

```bash
# 登录命令 - 通过 QR 码登录并保存 Cookie
bili-downloader login

# 下载命令 - 下载番剧视频
bili-downloader download
```

每个命令都有详细的帮助信息，可以通过 `--help` 参数查看：

```bash
bili-downloader --help
bili-downloader login --help
bili-downloader download --help
```

### 项目结构

```
bili_downloader_py/
├─ .env.example
├─ .gitignore
├─ CHANGELOG.md
├─ cookie.txt
├─ copilot-instructions.md
├─ LICENSE
├─ poetry.lock
├─ pyproject.toml
├─ QWEN.md
├─ README.md
├─ requirements-dev.txt
├─ requirements.txt
├─ bili_downloader/
│  ├─ __init__.py
│  ├─ core/             # 业务逻辑（无 CLI/GUI 依赖）
│  │  ├─ bangumi_downloader.py
│  │  ├─ downloader_aria2.py
│  │  ├─ downloader_axel.py
│  │  ├─ qrcode_login.py
│  │  └─ vamerger.py
│  ├─ cli/              # Typer CLI
│  │  ├─ __init__.py
│  │  ├─ main.py
│  │  ├─ cmd_download.py
│  │  └─ cmd_login.py
│  ├─ config/           # 配置管理
│  │  ├─ __init__.py
│  │  └─ settings.py
│  ├─ utils/            # 工具模块
│  │  └─ logger.py
│  └─ exceptions.py     # 自定义异常
├─ docs/
├─ examples/
├─ tests/
└─ venv/               # 虚拟环境（如果使用）
```

## ❓ 常见问题解答

### 1. 412 Precondition Failed 错误

此错误通常是由于缺少请求头部信息引起的。程序会自动添加以下头部信息：
- `User-Agent`：模拟浏览器请求。
- `Referer`：设置为哔哩哔哩的域名。
- `Accept`：接受所有内容类型。
- `Accept-Language`：支持英语和中文。
- `Accept-Encoding`：支持压缩格式。

如果此错误仍然存在，请检查：
- 您的 Cookie 是否有效且未过期？
- 剧集是否需要大会员？
- 您的网络连接是否稳定？

### 2. 下载失败

- 确保您的 Cookie 有效。
- 检查您的网络连接。
- 确认您有足够的存储空间。

### 3. 合并失败

- 检查 FFmpeg 是否正确安装。
- 确认音频和视频文件均已完全下载。

### 4. 下载速度慢

- 尝试增加线程数。
- 切换下载器 (axel/aria2)。
- 检查您的网络状况。

## 📜 许可证

该项目基于 MIT 许可证。有关详细信息，请参阅 [LICENSE](LICENSE) 文件。

## 🙏 致谢

特别感谢开源社区以及本项目所使用的库的开发者们。

## 参考与借鉴

该项目实现过程中主要参考借鉴了如下的项目，感谢他们的贡献：

+ [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect) B 站的第三方接口文档
+ [bilibili-api](https://github.com/Nemo2011/bilibili-api) 使用 Python 调用接口的参考实现
+ [danmu2ass](https://github.com/gwy15/danmu2ass) 本项目弹幕下载功能的缝合来源
