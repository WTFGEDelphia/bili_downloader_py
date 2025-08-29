# Bilibili番剧下载器使用指南

## 快速开始

1. **安装依赖**:
   ```bash
   pip install requests typer[all] rich structlog pydantic[dotenv] pydantic-settings
   ```

2. **安装外部工具**:
   - 安装 `ffmpeg` (用于音视频合并)
   - 安装 `aria2` 或 `axel` (用于下载)

3. **获取B站Cookie**:
   - 登录B站网站
   - 打开浏览器开发者工具(F12)
   - 在Network标签页刷新页面
   - 找到任意请求，复制Request Headers中的Cookie值
   - 将Cookie值保存到项目根目录的`cookie.txt`文件中

4. **运行下载器**:
   ```bash
   # 交互式下载
   python -m bili_downloader.cli.main download
   
   # 或者使用命令行参数
   python -m bili_downloader.cli.main download \
     --url "https://www.bilibili.com/bangumi/play/ep836727" \
     --directory "/path/to/download" \
     --quality 112 \
     --downloader axel \
     --cleanup
   ```

## 支持的URL格式

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

## 配置文件

程序会在用户配置目录创建配置文件 (`~/.config/bili-downloader/config.toml`)，您可以修改默认设置:

```toml
[download]
default_quality = 112
default_downloader = "axel"
default_threads = 16
cleanup_after_merge = false

[network]
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
```

## 环境变量配置

您也可以通过环境变量覆盖配置:

```bash
# 设置默认下载清晰度
export DOWNLOAD__DEFAULT_QUALITY=80

# 设置默认下载器
export DOWNLOAD__DEFAULT_DOWNLOADER=aria2

# 设置线程数
export DOWNLOAD__DEFAULT_THREADS=32
```

## 常见问题

### 1. 下载失败
- 检查Cookie是否有效
- 确认网络连接正常
- 确保有足够存储空间

### 2. 合并失败
- 检查ffmpeg是否正确安装
- 确认音视频文件完整下载

### 3. 下载速度慢
- 尝试增加线程数
- 更换下载器(axel/aria2)
- 检查网络状况

## 开发指南

### 运行测试
```bash
# 运行特定测试
python tests/test_sanitize_filename.py
```

### 代码格式化
```bash
# 格式化代码
black .
isort .
```

### 代码检查
```bash
# 代码检查
ruff check .
```