import os
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm

from bili_downloader.core.bangumi_downloader import (
    BangumiDownloader,
    QUALITY_OPTIONS,
)
from bili_downloader.config.settings import Settings
from bili_downloader.exceptions import (
    BiliDownloaderError,
    DownloadError,
    MergeError,
    APIError,
)
from bili_downloader.utils.logger import logger, configure_logger

app = typer.Typer()
console = Console()


def get_cookie():
    """尝试从文件读取 Cookie，如果失败则提示用户输入。"""
    cookie = ""
    # 尝试使用 __file__ 获取更可靠的脚本路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_file_path = os.path.join(script_dir, "..", "..", "cookie.txt")

    if os.path.exists(cookie_file_path):
        try:
            with open(cookie_file_path, "r") as f:
                cookie = f.read().strip()
        except Exception as e:
            console.print(
                f"Warning: Could not read cookie from {cookie_file_path}: {e}"
            )
            console.print("Please paste your cookie when prompted.")
    else:
        console.print(f"Info: Cookie file not found at {cookie_file_path}.")
        console.print("Please paste your cookie when prompted.")

    if not cookie:
        cookie = Prompt.ask("Please paste your Bilibili cookie").strip()
        if not cookie:
            console.print("[red]Error: Cookie is required.[/red]")
            raise typer.Exit(code=1)

    return BangumiDownloader({}, {}).convert_cookie_to_dict(cookie)


def get_user_input(settings: Settings):
    """获取用户输入的 URL、下载目录、清晰度选项、清理选项和下载器类型。"""
    # 从用户获取输入，如果直接回车则使用默认值
    video_url = Prompt.ask(
        "Enter Video URL",
        default="https://www.bilibili.com/bangumi/play/ep1231565?spm_id_from=333.1387.0.0",
    )

    record_url = Prompt.ask(
        "Enter Download Directory",
        # default=str(Path.home() / "Movies" / "bili_downloader"),
        default="G:/LLM/ghost_download/bilibili/video/凡人",
    )

    doclean = Confirm.ask(
        "Clean .flv/.ogg files after merging?",
        default=settings.download.cleanup_after_merge,
    )

    # 显示清晰度选项并获取用户选择
    console.print("\nAvailable quality options:")
    for qn, desc in QUALITY_OPTIONS.items():
        default_mark = " (default)" if qn == settings.download.default_quality else ""
        console.print(f"  {qn}: {desc}{default_mark}")

    while True:
        quality_choice = Prompt.ask(
            f"\nSelect quality (enter number)",
            default=str(settings.download.default_quality),
        ).strip()
        if not quality_choice:
            selected_qn = settings.download.default_quality
            break
        try:
            selected_qn = int(quality_choice)
            if selected_qn in QUALITY_OPTIONS:
                break
            else:
                console.print(
                    f"Please enter a valid quality number from the options above."
                )
        except ValueError:
            console.print("Please enter a valid number.")

    # 显示下载器选项并获取用户选择
    available_downloaders = ["axel", "aria2"]
    console.print("Available downloaders:")
    for i, dl in enumerate(available_downloaders, 1):
        default_mark = (
            " (default)" if dl == settings.download.default_downloader else ""
        )
        console.print(f"  {i}. {dl}{default_mark}")

    while True:
        downloader_choice = Prompt.ask(
            f"Select downloader (1-{len(available_downloaders)})",
            default="1" if settings.download.default_downloader == "axel" else "2",
        ).strip()
        if not downloader_choice:
            downloader_type = settings.download.default_downloader
            break
        try:
            choice_index = int(downloader_choice) - 1
            if 0 <= choice_index < len(available_downloaders):
                downloader_type = available_downloaders[choice_index]
                break
            else:
                console.print(
                    f"Please enter a number between 1 and {len(available_downloaders)}."
                )
        except ValueError:
            console.print("Please enter a valid number.")

    record_url = os.path.abspath(os.path.expanduser(record_url))

    # 简单验证目录路径（不检查父目录权限）
    if os.path.exists(record_url) and not os.path.isdir(record_url):
        console.print(f"[red]Error: {record_url} exists but is not a directory.[/red]")
        raise typer.Exit(code=1)

    return video_url, record_url, selected_qn, doclean, downloader_type


@app.command()
def download(
    url: str = typer.Option("", "--url", "-u", help="Video URL to download"),
    directory: str = typer.Option("", "--directory", "-d", help="Download directory"),
    quality: int = typer.Option(0, "--quality", "-q", help="Video quality"),
    cleanup: bool = typer.Option(False, "--cleanup", "-c", help="Clean up after merge"),
    downloader: str = typer.Option(
        "", "--downloader", "-D", help="Downloader to use (axel or aria2)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    """
    下载哔哩哔哩番剧

    从指定的 URL 下载哔哩哔哩番剧视频，并保存到指定目录。
    """
    # Configure logger
    configure_logger(verbose)

    try:
        # Load settings
        settings = Settings()

        # Cookie
        cookie = get_cookie()

        # Input
        if url and directory and quality > 0 and downloader:
            # 如果所有参数都通过命令行提供，则直接使用
            video_url = url
            record_url = directory
            selected_qn = quality
            doclean = cleanup
            downloader_type = downloader
        else:
            # 否则交互式获取用户输入
            video_url, record_url, selected_qn, doclean, downloader_type = (
                get_user_input(settings)
            )

        console.print(
            f"Downloading from {video_url} to {record_url} with quality {selected_qn} using {downloader_type}"
        )

        # Create downloader instance
        downloader_instance = BangumiDownloader(cookie)
        console.print(f"begin to get detail info")
        # Download with default headers
        info = downloader_instance.get_detailed_info_from_url(
            video_url, settings.network.headers
        )
        # print(f"\\nget detail info: {info}")
        # Pass the selected quality to the download function
        merged_files = downloader_instance.download_all_from_info_with_quality(
            info,
            record_url,
            selected_qn,
            doclean,
            settings.network.headers,
            downloader_type,
        )
        console.print(f"\\nDownload completed. Merged {len(merged_files)} files:")
        for file in merged_files:
            console.print(f"  - {file}")

    except KeyboardInterrupt:
        console.print("\\n[yellow]Download interrupted by user.[/yellow]")
        logger.info("Download interrupted by user")
        raise typer.Exit(code=1)
    except APIError as e:
        console.print(f"[red]API Error: {e}[/red]")
        logger.error("API Error", error=str(e))
        raise typer.Exit(code=1)
    except DownloadError as e:
        console.print(f"[red]Download Error: {e}[/red]")
        logger.error("Download Error", error=str(e))
        raise typer.Exit(code=1)
    except MergeError as e:
        console.print(f"[red]Merge Error: {e}[/red]")
        logger.error("Merge Error", error=str(e))
        raise typer.Exit(code=1)
    except BiliDownloaderError as e:
        console.print(f"[red]BiliDownloader Error: {e}[/red]")
        logger.error("BiliDownloader Error", error=str(e))
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        logger.error("An unexpected error occurred", error=str(e))
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
