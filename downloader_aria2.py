import os
import shutil
import subprocess


def find_executable(name):
    """在预定义路径或系统 PATH 中查找可执行文件。"""
    # 1. Check in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(script_dir, name)
    if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
        return exe_path

    # 2. Check with .exe extension (for Windows)
    exe_path_exe = exe_path + ".exe"
    if os.path.isfile(exe_path_exe) and os.access(exe_path_exe, os.X_OK):
        return exe_path_exe

    # 3. Fall back to checking system PATH
    system_exe = shutil.which(name)
    if system_exe:
        return system_exe

    # 4. Not found
    return None


# Find aria2c executable
aria2c_path = find_executable("aria2c")
if not aria2c_path:
    raise FileNotFoundError(
        "aria2c executable not found. Please ensure it is installed and in your PATH, or place it in the script directory."
    )


class DownloaderAria2:
    def __init__(self, url, num, dest, header=None, max_retry=3):
        self.url = url
        self.num = num
        self.dest = dest
        self.header = header if header is not None else {}
        self.max_retry = max_retry

    def run(self):
        """
        使用 aria2c 下载文件。
        返回 True 表示成功，False 表示失败。
        """
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(self.dest), exist_ok=True)

        # 构建 aria2c 命令参数列表
        cmd = [
            aria2c_path,
            "-x",
            str(self.num),  # 最大连接数
            "-s",
            str(self.num),  # 分段数量
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

        # Add headers
        for key, value in self.header.items():
            # 特殊处理 User-Agent 和 Referer
            if key.lower() == "user-agent":
                # Ensure the header value is properly formatted
                if isinstance(value, str):
                    escaped_value = value.replace('"', '\\"').replace("'", "\\'")
                    cmd.extend(["-U", escaped_value])
                else:
                    cmd.extend(["-U", str(value)])
            elif key.lower() == "referer":
                # Ensure the header value is properly formatted
                if isinstance(value, str):
                    escaped_value = value.replace('"', '\\"').replace("'", "\\'")
                    cmd.extend(["--referer", escaped_value])
                else:
                    cmd.extend(["--referer", str(value)])
            else:
                # 其他头部信息使用 --header 选项
                # Ensure the header value is properly formatted
                if isinstance(value, str):
                    escaped_value = value.replace('"', '\\"').replace("'", "\\'")
                    cmd.extend(["--header", f"{key}: {escaped_value}"])
                else:
                    cmd.extend(["--header", f"{key}: {value}"])

        # Add URL
        cmd.append(self.url)

        print(f"\nExecuting download command: {' '.join(cmd)}")

        for attempt in range(1, self.max_retry + 1):
            try:
                # Use subprocess.run to execute the command
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                )

                if result.returncode == 0:
                    print(f"Download successful: {self.dest}")
                    return True
                else:
                    print(
                        f"Attempt {attempt} failed for {self.url}. Return code: {result.returncode}"
                    )
                    print(f"Stdout: {result.stdout}")
                    print(f"Stderr: {result.stderr}")
                    # Don't break yet, will retry if attempts left

            except subprocess.SubprocessError as e:
                print(
                    f"Attempt {attempt} failed for {self.url} with SubprocessError: {e}"
                )
            except Exception as e:
                print(
                    f"Attempt {attempt} failed for {self.url} with unexpected error: {e}"
                )

            if attempt < self.max_retry:
                print(f"Retrying... ({attempt}/{self.max_retry})")
            else:
                print(f"All {self.max_retry} attempts failed for {self.url}.")

        return False
