# Bilibili Bangumi Downloader

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/dependency%20manager-Poetry-blue)](https://python-poetry.org/)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-blue)

A powerful and user-friendly command-line tool for downloading Bilibili bangumi (anime) videos with high quality and efficiency.

## 🌟 Features

- **High-Quality Downloads**: Support for multiple video qualities including 1080P+, 4K, HDR, and Dolby Vision (requires Bilibili Premium).
- **Flexible Downloaders**: Choose between `aria2` and `axel` for optimized download speeds.
- **Smart Merging**: Automatically merges downloaded audio and video streams into a single `.mkv` file.
- **Keyword Filtering**: Download only episodes whose titles contain a specific keyword.
- **Configurable & Persistent**: Save your preferences and history using TOML config files and environment variables.
- **Docker Support**: Run the downloader in an isolated container environment for easy setup and deployment.
- **Detailed Logging**: Structured logging with `structlog` for easy debugging and monitoring.
- **Modular Design**: Easy to extend and maintain, built with Python best practices.

## 📦 Installation

### Prerequisites

Before installing the Bilibili Bangumi Downloader, ensure you have the following installed on your system:

- **Python 3.11 or higher** ([Download Python](https://www.python.org/downloads/))
- **Poetry** (recommended for dependency management) - [Installation Guide](https://python-poetry.org/docs/#installation)
- **FFmpeg** (for merging audio and video) - [Download FFmpeg](https://ffmpeg.org/download.html)
- **Aria2 or Axel** (optional, for accelerated downloads) - Install via your system's package manager or download from their official sites.

### Option 1: Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/WTFGEDelphia/bili_downloader_py.git
cd bili_downloader_py

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell

# Run the program
bili-downloader download
```

### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/WTFGEDelphia/bili_downloader_py.git
cd bili_downloader_py

# (Optional but recommended) Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# Or
.venv\\Scripts\\activate     # Windows

# Install the package
pip install .

# Run the program
bili-downloader download
```

### Option 3: Using Docker (Recommended for Isolation)

```bash
# Build the Docker image
docker build -t bili-downloader .

# Run interactively
docker run -it --rm \\
  -v $(pwd)/downloads:/app/downloads \\
  -v $(pwd)/cookie.txt:/app/cookie.txt:ro \\
  bili-downloader download

# Or download a specific episode directly
docker run -it --rm \\
  -v $(pwd)/downloads:/app/downloads \\
  -v $(pwd)/cookie.txt:/app/cookie.txt:ro \\
  bili-downloader download \\
  --url "https://www.bilibili.com/bangumi/play/ep836727" \\
  --directory "/app/downloads" \\
  --quality 112

# Using environment variables for configuration
docker run -it --rm \\
  -v $(pwd)/downloads:/app/downloads \\
  -v $(pwd)/cookie.txt:/app/cookie.txt:ro \\
  -e DOWNLOAD__DEFAULT_DOWNLOADER=aria2 \\
  -e DOWNLOAD__DEFAULT_QUALITY=80 \\
  bili-downloader download
```

### Option 4: Using Docker Compose (Recommended for Ease of Use)

```bash
# Build and run interactively
docker-compose run --rm bili-downloader download

# Download a specific episode directly
docker-compose run --rm bili-downloader download \\
  --url "https://www.bilibili.com/bangumi/play/ep836727" \\
  --directory "/app/downloads" \\
  --quality 112

# Edit `docker-compose.yml` to set default command for automated downloads
# 1. Modify the `command` line in `docker-compose.yml`:
#    command: ["download", "--url", "YOUR_VIDEO_URL_HERE", "--directory", "/app/downloads", "--quality", "112", "--downloader", "axel"]
# 2. Run:
#    docker-compose run --rm bili-downloader
```

## 🚀 Quick Start

### 1. Get Your Bilibili Cookie

To download videos, you need a valid Bilibili account cookie.

1. Log in to [Bilibili](https://www.bilibili.com/).
2. Open your browser's Developer Tools (F12).
3. Go to the Network tab and refresh the page.
4. Find any request, right-click, and select "Copy" > "Copy Request Headers".
5. Extract the `Cookie` value from the copied headers.
6. Save this cookie value to a file named `cookie.txt` in the project's root directory.

### 2. Run the Downloader

#### Interactive Mode (Recommended for Beginners)

```bash
bili-downloader download
```

The program will prompt you for:
- Video URL (Bangumi homepage or episode page)
- Download directory
- Keyword filter (optional)
- Video quality
- Downloader (aria2 or axel)
- Whether to clean up original files after merging

#### Command-Line Mode (For Scripts/Automation)

```bash
bili-downloader download \\
  --url "https://www.bilibili.com/bangumi/play/ep836727" \\
  --directory "./downloads" \\
  --quality 112 \\
  --downloader axel \\
  --cleanup \\
  --keyword "cli"
```

#### Enable Verbose Logging

```bash
bili-downloader download --verbose
# Or
bili-downloader download -v
```

### 3. Quick Examples

After creating your `cookie.txt` file, you can run:

```bash
# Interactive download
bili-downloader download

# Download a specific episode
bili-downloader download \\
  --url "https://www.bilibili.com/bangumi/play/ep836727" \\
  --directory "./downloads" \\
  --quality 112

# Download only episodes with "战斗" (battle) in the title
bili-downloader download \\
  --url "https://www.bilibili.com/bangumi/play/ep836727" \\
  --directory "./downloads" \\
  --quality 112 \\
  --keyword "战斗"
```

## 📚 Supported URL Formats

- **Bangumi Homepage**: `https://www.bilibili.com/bangumi/media/md191`
- **Episode Page**: `https://www.bilibili.com/bangumi/play/ep836727`

## 📺 Video Quality Options

| Code | Description                      |
|------|----------------------------------|
| 6    | 240P Extreme (MP4 only)          |
| 16   | 360P Smooth (Default minimum)    |
| 32   | 480P Clear (No login required)   |
| 64   | 720P HD (Login required)         |
| 74   | 720P60 High Frame Rate (Login)   |
| 80   | 1080P HD (Login required)        |
| 112  | 1080P+ High Bitrate (Premium)    |
| 116  | 1080P60 High Frame Rate (Premium)|
| 120  | 4K Ultra HD (Premium)            |
| 125  | HDR True Color (Premium)         |
| 126  | Dolby Vision (Premium)           |
| 127  | 8K Ultra HD (Premium)            |

## ⚙️ Configuration

The downloader supports configuration through multiple methods, with the following priority (highest to lowest):

1. Command-line arguments
2. Environment variables
3. Configuration file (`~/.config/bili-downloader/config.toml`)
4. `.env` file
5. Built-in defaults

### Configuration File

On first run, the program will create a default configuration file:
- **Linux/macOS**: `~/.config/bili-downloader/config.toml`
- **Windows**: `C:\\Users\\{username}\\AppData\\Roaming\\bili-downloader\\config.toml`

Example `config.toml`:

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

The program will automatically save the last used URL and download directory, which will be used as defaults in subsequent runs.

### Environment Variables

You can also configure the program using environment variables:

```bash
# Set default download quality
export DOWNLOAD__DEFAULT_QUALITY=80

# Set default downloader
export DOWNLOAD__DEFAULT_DOWNLOADER=aria2

# Set number of threads
export DOWNLOAD__DEFAULT_THREADS=32

# Set default URL (overrides history)
export DOWNLOAD__DEFAULT_URL="https://www.bilibili.com/bangumi/play/ep123"

# Set default directory (overrides history)
export DOWNLOAD__DEFAULT_DIRECTORY="/path/to/downloads"

# Set whether to clean up after merging
export DOWNLOAD__CLEANUP_AFTER_MERGE=true
```

Environment variables take precedence over history records and default settings in the config file.

### .env File

Copy the `.env.example` file to `.env` and modify it as needed:

```bash
cp .env.example .env
```

## 🛠️ Dependencies

### Python Dependencies

- Python 3.11+
- requests
- typer[all]
- rich
- structlog
- pydantic[dotenv]
- pydantic-settings
- toml

### External Tools

- **FFmpeg**: Required for merging audio and video streams.
- **Aria2** (optional): For accelerated downloads using the `aria2` downloader.
- **Axel** (optional): For accelerated downloads using the `axel` downloader.

Ensure these tools are installed and available in your system PATH, or place them in the script's directory.

## 🧪 Development

### Code Formatting and Checking

```bash
# Format code
poetry run black .
poetry run isort .

# Check code
poetry run ruff check .

# Run tests
poetry run pytest
```

### Project Structure

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
│  ├─ core/             # Business logic (no CLI/GUI dependencies)
│  │  ├─ bangumi_downloader.py
│  │  ├─ downloader_aria2.py
│  │  ├─ downloader_axel.py
│  │  └─ vamerger.py
│  ├─ cli/              # Typer CLI
│  │  ├─ __init__.py
│  │  ├─ main.py
│  │  └─ cmd_download.py
│  ├─ config/           # Configuration management
│  │  ├─ __init__.py
│  │  └─ settings.py
│  ├─ utils/            # Utility modules
│  │  └─ logger.py
│  └─ exceptions.py     # Custom exceptions
├─ docs/
├─ examples/
├─ tests/
└─ venv/               # Virtual environment (if used)
```

## ❓ FAQ

### 1. 412 Precondition Failed Error

This error usually occurs due to missing request headers. The program automatically adds the following headers:
- `User-Agent`: Simulates a browser request.
- `Referer`: Set to Bilibili's domain.
- `Accept`: Accepts all content types.
- `Accept-Language`: Supports English and Chinese.
- `Accept-Encoding`: Supports compressed formats.

If this error persists, check:
- Is your Cookie valid and not expired?
- Does the episode require Premium membership?
- Is your network connection stable?

### 2. Download Failures

- Ensure your Cookie is valid.
- Check your network connection.
- Verify you have sufficient storage space.

### 3. Merge Failures

- Check if FFmpeg is correctly installed.
- Confirm that both audio and video files are fully downloaded.

### 4. Slow Download Speed

- Try increasing the number of threads.
- Switch downloaders (axel/aria2).
- Check your network conditions.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

Special thanks to the open-source community and the developers of the libraries used in this project.