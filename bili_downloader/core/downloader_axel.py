import os
import shutil
import subprocess

from bili_downloader.utils.logger import logger
from bili_downloader.utils.print_utils import print_warning


def find_executable(name):
    """在预定义路径或系统 PATH 中查找可执行文件。"""
    # 1. 首先检查环境变量 (例如, AXEL_PATH)
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


# 查找axel可执行文件
axel_path = find_executable("axel")
if not axel_path:
    axel_path = None
    print_warning("未找到axel可执行文件。axel下载器将无法工作。")


class DownloaderAxel:
    def __init__(self, url, num, dest, header=None, max_retry=3):
        self.url = url
        self.num = num
        self.dest = dest
        self.header = header if header is not None else {}
        self.max_retry = max_retry

    def run(self):
        """
        使用 axel 下载文件。
        返回 True 表示成功，False 表示失败。
        """
        # 确保下载器可用
        if axel_path is None:
            logger.error("未找到Axel可执行文件。无法下载文件。")
            return False

        # 确保目标目录存在
        os.makedirs(os.path.dirname(self.dest), exist_ok=True)

        # 清除可能存在的不完整状态文件
        state_file = self.dest + ".st"
        if os.path.exists(state_file):
            try:
                os.remove(state_file)
            except Exception as e:
                logger.warning(f"无法移除状态文件 {state_file}", error=str(e))

        # 构建 axel 命令参数列表
        cmd = [
            axel_path,
            "-n",
            str(self.num),  # 最大连接数
            "-o",
            self.dest,  # 输出文件名
        ]

        # 添加请求头
        user_agent = None
        referer = None
        other_headers = {}

        for key, value in self.header.items():
            key_lower = key.lower()
            if key_lower == "user-agent":
                user_agent = value
            elif key_lower == "referer":
                referer = value
            else:
                other_headers[key] = value

        # 使用 -U 参数设置 User-Agent
        if user_agent:
            if isinstance(user_agent, str):
                cmd.extend(["-U", user_agent])
            else:
                cmd.extend(["-U", str(user_agent)])

        # 使用 -H 参数设置 Referer 和其他头部
        if referer:
            if isinstance(referer, str):
                cmd.extend(["-H", f"Referer: {referer}"])
            else:
                cmd.extend(["-H", f"Referer: {referer}"])

        # 添加其他头部信息
        for key, value in other_headers.items():
            if isinstance(value, str):
                cmd.extend(["-H", f"{key}: {value}"])
            else:
                cmd.extend(["-H", f"{key}: {value}"])

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
                    timeout=300,  # 设置5分钟超时
                )

                if result.returncode == 0:
                    logger.info("Download successful", dest=self.dest)
                    return True
                else:
                    logger.warning(
                        f"尝试 {attempt} 失败，URL: {self.url}。返回码: {result.returncode}",
                        stderr=result.stderr,
                    )
                    # 不立即退出，如果还有重试次数则继续

            except subprocess.TimeoutExpired:
                logger.error(f"尝试 {attempt} 超时，URL: {self.url}")
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
