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


# Find axel executable
axel_path = find_executable("axel")
if not axel_path:
    raise FileNotFoundError(
        "axel executable not found. Please ensure it is installed and in your PATH, or place it in the script directory."
    )


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
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(self.dest), exist_ok=True)

        # 清除可能存在的不完整状态文件
        state_file = self.dest + ".st"
        if os.path.exists(state_file):
            try:
                os.remove(state_file)
            except Exception as e:
                print(f"Warning: Could not remove state file {state_file}: {e}")

        # 构建 axel 命令参数列表
        cmd = [
            axel_path,
            "-k",  # 不检查证书（避免SSL问题）
            "-c",  # Skip download if file already exists
            "-p",  # Print simple percentages instead of progress bar (0-100)
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
                escaped_user_agent = user_agent.replace('"', '\\"').replace("'", "\\'")
                cmd.extend(["-U", escaped_user_agent])
            else:
                cmd.extend(["-U", str(user_agent)])

        # 使用 -H 参数设置 Referer 和其他头部
        if referer:
            if isinstance(referer, str):
                escaped_referer = referer.replace('"', '\\"').replace("'", "\\'")
                cmd.extend(["-H", f"Referer: {escaped_referer}"])
            else:
                cmd.extend(["-H", f"Referer: {referer}"])

        # 添加其他头部信息
        for key, value in other_headers.items():
            if isinstance(value, str):
                escaped_value = value.replace('"', '\\"').replace("'", "\\'")
                cmd.extend(["-H", f"{key}: {escaped_value}"])
            else:
                cmd.extend(["-H", f"{key}: {value}"])

        # Add URL
        cmd.append(self.url)

        print(f"Executing download command: {' '.join(cmd)}")

        for attempt in range(1, self.max_retry + 1):
            try:
                # Use subprocess.run to execute the command
                # stdout and stderr are captured but not printed by default unless there's an error
                # You can redirect them to DEVNULL if you don't want to see axel's progress
                # result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
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
