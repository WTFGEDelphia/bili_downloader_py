class BiliDownloaderError(Exception):
    """BiliDownloader 的基础异常类"""

    pass


class DownloadError(BiliDownloaderError):
    """下载相关错误"""

    pass


class MergeError(BiliDownloaderError):
    """合并相关错误"""

    pass


class APIError(BiliDownloaderError):
    """API 调用相关错误"""

    pass
