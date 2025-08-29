# 环境变量配置说明

## 概述

B站番剧下载器支持通过`.env`文件和操作系统的环境变量来配置各种设置。这种方式允许用户在不修改代码的情况下自定义程序行为。

## 配置文件

项目根目录提供了 `.env.example` 文件作为配置示例。用户可以复制此文件为 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

## 环境变量说明

### 下载设置

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `DOWNLOAD__DEFAULT_QUALITY` | 112 | 默认下载清晰度 |
| `DOWNLOAD__DEFAULT_DOWNLOADER` | axel | 默认下载器 (axel 或 aria2) |
| `DOWNLOAD__DEFAULT_THREADS` | 16 | 默认下载线程数 |
| `DOWNLOAD__CLEANUP_AFTER_MERGE` | false | 合并后是否清理原始音视频文件 |

### 网络设置

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `NETWORK__USER_AGENT` | Chrome浏览器标识 | 请求使用的 User-Agent |

### 下载器路径设置

如果下载器没有安装在系统PATH中，可以通过以下环境变量指定可执行文件的完整路径：

| 环境变量 | 说明 |
|---------|------|
| `ARIA2C_PATH` | aria2c 可执行文件的完整路径 |
| `AXEL_PATH` | axel 可执行文件的完整路径 |

示例：
```bash
# Windows
set ARIA2C_PATH=C:\tools\aria2\aria2c.exe
set AXEL_PATH=C:\tools\axel\axel.exe

# Linux/macOS
export ARIA2C_PATH=/usr/local/bin/aria2c
export AXEL_PATH=/usr/local/bin/axel
```

## 清晰度选项

支持的清晰度代码：
- 6: 240P 极速
- 16: 360P 流畅
- 32: 480P 清晰
- 64: 720P 高清
- 74: 720P60 高帧率
- 80: 1080P 高清
- 112: 1080P+ 高码率 (默认)
- 116: 1080P60 高帧率
- 120: 4K 超清
- 125: HDR 真彩
- 126: 杜比视界
- 127: 8K 超高清

## 使用示例

### 1. 基本配置
```bash
# .env
DOWNLOAD__DEFAULT_QUALITY=80
DOWNLOAD__DEFAULT_DOWNLOADER=aria2
DOWNLOAD__DEFAULT_THREADS=32
```

### 2. 高级配置（指定下载器路径）
```bash
# .env
DOWNLOAD__DEFAULT_QUALITY=120
DOWNLOAD__DEFAULT_DOWNLOADER=axel
DOWNLOAD__DEFAULT_THREADS=64
DOWNLOAD__CLEANUP_AFTER_MERGE=true
NETWORK__USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
ARIA2C_PATH=/custom/path/to/aria2c
AXEL_PATH=/custom/path/to/axel
```

### 3. 操作系统环境变量配置
```bash
# Windows CMD
set DOWNLOAD__DEFAULT_QUALITY=80
set ARIA2C_PATH=C:\tools\aria2\aria2c.exe

# Windows PowerShell
$env:DOWNLOAD__DEFAULT_QUALITY="80"
$env:ARIA2C_PATH="C:\tools\aria2\aria2c.exe"

# Linux/macOS
export DOWNLOAD__DEFAULT_QUALITY=80
export ARIA2C_PATH=/custom/path/to/aria2c
```

## 优先级

配置的优先级从高到低为：
1. 操作系统环境变量
2. .env 文件
3. 默认值

## 注意事项

1. `.env` 文件不会被提交到版本控制系统中（已被.gitignore忽略）
2. 环境变量名使用双下划线 `__` 作为嵌套分隔符
3. 布尔值可以使用 true/false, 1/0, yes/no 等形式
4. 修改.env文件或环境变量后需要重新运行程序才能生效
5. 下载器路径环境变量(`ARIA2C_PATH`, `AXEL_PATH`)的优先级高于系统PATH中的同名可执行文件