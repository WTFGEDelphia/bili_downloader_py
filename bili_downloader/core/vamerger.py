import os
import shutil
import subprocess

from bili_downloader.utils.logger import logger


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


# Find ffmpeg executable
ffmpeg_path = find_executable("ffmpeg")
if not ffmpeg_path:
    ffmpeg_path = None
    print("Warning: ffmpeg executable not found. Video/audio merging will not work.")


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
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output), exist_ok=True)

        # 构建 ffmpeg 命令参数列表
        # -y 选项用于覆盖输出文件（如果已存在）
        cmd = [
            ffmpeg_path,
            "-y",  # Overwrite output files without asking
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
            # "-c:v", "copy",     # Copy video stream
            # "-c:a", "copy",      # Copy audio stream
            # "-strict", "experimental", # Required for AAC encoding in some ffmpeg versions
            self.output,
        ]

        logger.info("Executing merge command", command=" ".join(cmd))

        try:
            # Use subprocess.run to execute the command
            # Capture stdout and stderr for logging
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
                    f"Merge failed for {self.output}. Return code: {result.returncode}",
                    stderr=result.stderr,
                )
                return False

        except subprocess.SubprocessError as e:
            logger.error(f"Merge failed for {self.output} with SubprocessError", error=str(e))
            return False
        except Exception as e:
            logger.error(f"Merge failed for {self.output} with unexpected error", error=str(e))
            return False