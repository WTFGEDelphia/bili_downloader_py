import os
import shutil
import subprocess

from bili_downloader.utils.logger import logger
from bili_downloader.utils.print_utils import print_warning


def find_executable(name):
    """在预定义路径或系统 PATH 中查找可执行文件。"""
    # 1. 检查脚本同目录下
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(script_dir, name)
    if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
        return exe_path

    # 2. 检查.exe扩展名 (适用于Windows)
    exe_path_exe = exe_path + ".exe"
    if os.path.isfile(exe_path_exe) and os.access(exe_path_exe, os.X_OK):
        return exe_path_exe

    # 3. 回退到检查系统PATH
    system_exe = shutil.which(name)
    if system_exe:
        return system_exe

    # 4. 未找到
    return None


# 查找ffmpeg可执行文件
ffmpeg_path = find_executable("ffmpeg")
if not ffmpeg_path:
    ffmpeg_path = None
    print_warning("未找到ffmpeg可执行文件。视频/音频合并将无法工作。")


class VAMerger:
    def __init__(self, audio, video, output):
        self.audio = audio
        self.video = video
        self.output = output

    def run(self):
        """
        使用 ffmpeg 合并音频和视频文件。
        返回 True 表示成功，False 表示失败。
        """
        # 确保输出目录存在
        os.makedirs(os.path.dirname(self.output), exist_ok=True)

        # 确保下载器可用
        if ffmpeg_path is None:
            logger.error("未找到FFmpeg可执行文件。无法合并文件。")
            return False

        # 构建 ffmpeg 命令参数列表
        # -y 选项用于覆盖输出文件（如果已存在）
        cmd = [
            ffmpeg_path,
            "-y",  # 覆盖输出文件而不询问
            "-i",
            self.video,
            "-i",
            self.audio,
            "-c",
            "copy",
            "-map",
            "0:v",
            "-map",
            "1:a",
            # "-c:v", "copy",     # 复制视频流
            # "-c:a", "copy",      # 复制音频流
            # "-strict", "experimental", # 某些ffmpeg版本中AAC编码所需
            self.output,
        ]

        logger.info("正在执行合并命令", command=" ".join(cmd))

        try:
            # 使用 subprocess.run 执行命令
            # 捕获 stdout 和 stderr 用于日志记录
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            if result.returncode == 0:
                logger.info("Merge successful", output=self.output)
                return True
            else:
                logger.error(
                    f"合并失败，输出文件: {self.output}。返回码: {result.returncode}",
                    stderr=result.stderr,
                )
                return False

        except subprocess.SubprocessError as e:
            logger.error(f"合并失败，输出文件: {self.output}，子进程错误", error=str(e))
            return False
        except Exception as e:
            logger.error(f"合并失败，输出文件: {self.output}，意外错误", error=str(e))
            return False
