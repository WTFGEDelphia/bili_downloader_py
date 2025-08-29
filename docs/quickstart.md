# 快速入门指南

## 1. 环境准备

确保您已安装：
- Python 3.11+
- ffmpeg (用于音视频合并)
- aria2 或 axel (用于下载)

## 2. 安装步骤

```bash
# 克隆项目
git clone https://github.com/WTFGEDelphia/bili_downloader_py.git
cd bili_downloader_py

# 安装Python依赖
pip install requests typer[all] rich structlog pydantic[dotenv] pydantic-settings

# 或使用pip安装所有依赖
pip install -r requirements.txt
```

## 3. 配置Cookie

1. 登录B站网站
2. 按F12打开开发者工具
3. 刷新页面，在Network标签页找到任意请求
4. 复制Request Headers中的Cookie值
5. 将Cookie保存到项目根目录的`cookie.txt`文件中

## 4. 开始下载

### 交互式下载（推荐）

```bash
bili-downloader download
```

按照提示输入：
- 视频URL
- 下载目录
- 清晰度
- 下载器类型

### 命令行下载

```bash
bili-downloader download \
  --url "https://www.bilibili.com/bangumi/play/ep836727" \
  --directory "./downloads" \
  --quality 112 \
  --downloader axel
```

## 5. 查看结果

下载的文件将保存在您指定的目录中，文件名会包含剧集标题和清晰度信息。

## 常见问题

### 找不到命令
如果 `bili-downloader` 命令不可用，可以直接运行：
```bash
python -m bili_downloader.cli.main download
```

### 下载失败
- 检查Cookie是否过期
- 确认网络连接正常
- 检查目标目录是否有写入权限

### 合并失败
- 确认ffmpeg已正确安装并在PATH中
- 检查磁盘空间是否充足