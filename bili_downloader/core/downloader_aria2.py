import os
import shutil
import subprocess

from bili_downloader.utils.logger import logger
from bili_downloader.utils.print_utils import print_warning


def find_executable(name):
    """在预定义路径或系统 PATH 中查找可执行文件。"""
    # 1. 首先检查环境变量 (例如, ARIA2C_PATH)
    env_var_name = f"{name.upper()}_PATH"
    env_path = os.environ.get(env_var_name)
    if env_path and os.path.isfile(env_path) and os.access(env_path, os.X_OK):
        return env_path

    # 2. 检查脚本同目录下
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(script_dir, name)
    if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
        return exe_path

    # 3. 检查.exe扩展名 (适用于Windows)
    exe_path_exe = exe_path + ".exe"
    if os.path.isfile(exe_path_exe) and os.access(exe_path_exe, os.X_OK):
        return exe_path_exe

    # 4. 检查系统PATH
    system_path = shutil.which(name)
    if system_path:
        return system_path

    # 5. 检查系统PATH中的.exe扩展名 (适用于Windows)
    system_path_exe = shutil.which(f"{name}.exe")
    if system_path_exe:
        return system_path_exe

    return None


# 查找aria2c可执行文件
aria2c_path = find_executable("aria2c")
if not aria2c_path:
    aria2c_path = None
    print_warning("未找到aria2c可执行文件。aria2下载器将无法工作。")


class DownloaderAria2:
    def __init__(self, url, num, dest, header=None, max_retry=3):
        self.url = url
        self.num = num if num <= 16 else 16
        self.dest = dest
        self.header = header if header is not None else {}
        self.max_retry = max_retry

    def run(self):
        """
        使用 aria2c 下载文件。
        返回 True 表示成功，False 表示失败。
        """
        # 确保下载器可用
        if aria2c_path is None:
            logger.error("未找到Aria2c可执行文件。无法下载文件。")
            return False

        # 确保目标目录存在
        os.makedirs(os.path.dirname(self.dest), exist_ok=True)

        # 构建 aria2c 命令参数列表
        cmd = [
            aria2c_path,
            "-x",
            str(self.num),  # 最大连接数 1-16
            "-s",
            str(self.num),  # 分段数量 1-*, default 5
            "-k",
            "1M",  # 分段最小大小
            "-o",
            os.path.basename(self.dest),  # 输出文件名
            "-d",
            os.path.dirname(self.dest),  # 输出目录
            "--continue=true",  # 断点续传
            "--auto-file-renaming=false",  # 不自动重命名
            "--allow-overwrite=true",  # 允许覆盖
            "--check-certificate=false",  # 不检查证书（避免SSL问题）
            "--console-log-level=warn",  # 减少控制台输出
            "--summary-interval=0",  # 禁用摘要输出
            "--retry-wait=1",  # 重试等待时间
            "--max-tries=0",  # 无限重试直到成功
        ]

        # 添加请求头
        for key, value in self.header.items():
            # 特殊处理 User-Agent 和 Referer
            if key.lower() == "user-agent":
                # 确保请求头值正确格式化
                if isinstance(value, str):
                    escaped_value = value.replace('"', '"').replace("'", "'")
                    cmd.extend(["-U", escaped_value])
                else:
                    cmd.extend(["-U", str(value)])
            elif key.lower() == "referer":
                # 确保请求头值正确格式化
                if isinstance(value, str):
                    escaped_value = value.replace('"', '"').replace("'", "'")
                    cmd.extend(["--referer", escaped_value])
                else:
                    cmd.extend(["--referer", str(value)])
            else:
                # 其他头部信息使用 --header 选项
                # 确保请求头值正确格式化
                if isinstance(value, str):
                    escaped_value = value.replace('"', '"').replace("'", "'")
                    cmd.extend(["--header", f"{key}: {escaped_value}"])
                else:
                    cmd.extend(["--header", f"{key}: {value}"])

        # 添加URL
        cmd.append(self.url)

        logger.info("正在执行下载命令", command=" ".join(cmd))

        for attempt in range(1, self.max_retry + 1):
            try:
                # 使用 subprocess.run 执行命令
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                )

                if result.returncode == 0:
                    logger.info("Download successful", dest=self.dest)
                    return True
                else:
                    logger.warning(
                        f"尝试 {attempt} 失败，URL: {self.url}。返回码: {result.returncode}",
                        stdout=result.stdout,
                        stderr=result.stderr,
                    )
                    # 不立即退出，如果还有重试次数则继续

            except subprocess.SubprocessError as e:
                logger.error(
                    f"尝试 {attempt} 失败，URL: {self.url}，子进程错误",
                    error=str(e),
                )
            except Exception as e:
                logger.error(
                    f"尝试 {attempt} 失败，URL: {self.url}，意外错误",
                    error=str(e),
                )

            if attempt < self.max_retry:
                logger.info(f"正在重试... ({attempt}/{self.max_retry})")
            else:
                logger.error(f"所有 {self.max_retry} 次尝试均已失败，URL: {self.url}.")
        return False
