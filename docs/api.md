# API 文档

## 核心模块

### BangumiDownloader

`bili_downloader.core.bangumi_downloader.BangumiDownloader`

这是主要的下载器类，负责处理哔哩哔哩番剧的下载逻辑。

#### 初始化

```python
downloader = BangumiDownloader(cookie, headers=None)
```

- `cookie`: Bilibili 网站的 Cookie 字典
- `headers`: 可选的 HTTP 请求头字典

#### 方法

##### `get_detailed_info_from_url(url, headers=None)`

根据 URL 解析并获取番剧详细信息。

- `url`: 番剧页面的 URL
- `headers`: 可选的 HTTP 请求头字典
- 返回: 包含番剧详细信息的字典

##### `download_all_from_info_with_quality(info, destdir, quality=DEFAULT_QN, doclean=False, headers=None, downloader_type=DEFAULT_DOWNLOADER)`

根据番剧信息下载所有集数并合并。

- `info`: `get_detailed_info_from_url` 返回的番剧信息
- `destdir`: 下载目录
- `quality`: 下载清晰度
- `doclean`: 合并后是否清理原始音视频文件
- `headers`: HTTP 请求头
- `downloader_type`: 下载器类型 ("axel" 或 "aria2")
- 返回: 合并后的文件路径列表

## 配置模块

### Settings

`bili_downloader.config.settings.Settings`

配置管理类，用于加载和管理应用程序的配置。

#### 属性

- `download`: 下载相关配置
  - `default_quality`: 默认下载清晰度
  - `default_downloader`: 默认下载器
  - `default_threads`: 默认下载线程数
  - `cleanup_after_merge`: 合并后是否清理原始音视频文件
- `network`: 网络相关配置
  - `user_agent`: User-Agent 字符串
  - `headers`: 默认请求头

## CLI 模块

### download

`bili_downloader.cli.main.download`

下载哔哩哔哩番剧的 CLI 命令。

#### 参数

- `--url, -u`: 视频 URL
- `--directory, -d`: 下载目录
- `--quality, -q`: 视频清晰度
- `--cleanup, -c`: 合并后清理原始文件
- `--downloader, -D`: 下载器类型