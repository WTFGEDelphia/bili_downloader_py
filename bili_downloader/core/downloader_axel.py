import os
import shutil
import subprocess

from bili_downloader.utils.logger import logger


def find_executable(name):
    """在预定义路径或系统 PATH 中查找可执行文件。"""
    # 1. Check environment variable first (e.g., AXEL_PATH)
    env_var_name = f"{name.upper()}_PATH"
    env_path = os.environ.get(env_var_name)
    if env_path and os.path.isfile(env_path) and os.access(env_path, os.X_OK):
        return env_path

    # 2. Check in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(script_dir, name)
    if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
        return exe_path

    # 3. Check with .exe extension (for Windows)
    exe_path_exe = exe_path + ".exe"
    if os.path.isfile(exe_path_exe) and os.access(exe_path_exe, os.X_OK):
        return exe_path_exe

    # 4. Check in system PATH
    system_path = shutil.which(name)
    if system_path:
        return system_path

    # 5. Check with .exe extension in system PATH (for Windows)
    system_path_exe = shutil.which(f"{name}.exe")
    if system_path_exe:
        return system_path_exe

    return None


# Find axel executable
axel_path = find_executable("axel")
if not axel_path:
    axel_path = None
    print("Warning: axel executable not found. axel downloader will not work.")


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
            logger.error("Axel executable not found. Cannot download file.")
            return False

        # Ensure destination directory exists
        os.makedirs(os.path.dirname(self.dest), exist_ok=True)

        # 清除可能存在的不完整状态文件
        state_file = self.dest + ".st"
        if os.path.exists(state_file):
            try:
                os.remove(state_file)
            except Exception as e:
                logger.warning(
                    f"Could not remove state file {state_file}", error=str(e)
                )

        # 构建 axel 命令参数列表
        cmd = [
            axel_path,
            "-n",
            str(self.num),  # 最大连接数
            "-o",
            self.dest,  # 输出文件名
        ]

        # Add headers
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

        # Add URL
        cmd.append(self.url)

        logger.info("Executing download command", command=" ".join(cmd))

        for attempt in range(1, self.max_retry + 1):
            try:
                # Use subprocess.run to execute the command
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
                        f"Attempt {attempt} failed for {self.url}. Return code: {result.returncode}",
                        stderr=result.stderr,
                    )
                    # Don't break yet, will retry if attempts left

            except subprocess.TimeoutExpired:
                logger.error(f"Attempt {attempt} timed out for {self.url}")
            except subprocess.SubprocessError as e:
                logger.error(
                    f"Attempt {attempt} failed for {self.url} with SubprocessError",
                    error=str(e),
                )
            except Exception as e:
                logger.error(
                    f"Attempt {attempt} failed for {self.url} with unexpected error",
                    error=str(e),
                )

            if attempt < self.max_retry:
                logger.info(f"Retrying... ({attempt}/{self.max_retry})")
            else:
                logger.error(f"All {self.max_retry} attempts failed for {self.url}.")

        return False
