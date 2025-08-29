# 用户指南

## 安装

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

## 配置

程序会在用户配置目录创建配置文件 (`~/.config/bili-downloader/config.toml`)，您可以修改默认设置:

```toml
[bili-downloader.download]
default_quality = 112
default_downloader = "axel"
default_threads = 16
cleanup_after_merge = false

[bili-downloader.network]
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
```

## 使用

1. 获取 Bilibili Cookie:
   - 登录 Bilibili 网站
   - 打开浏览器开发者工具 (F12)
   - 在 Network 标签页刷新页面
   - 找到任意请求，复制 Request Headers 中的 Cookie 值
   - 将 Cookie 值保存到 `cookie.txt` 文件中

2. 运行下载命令:
   ```bash
   bili-downloader download
   ```
   程序会交互式地提示您输入视频 URL、下载目录等信息。

   您也可以直接通过命令行参数指定:
   ```bash
   bili-downloader download --url <视频URL> --directory <下载目录> --quality <清晰度> --downloader <下载器>
   ```