import os
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from bili_downloader.cli.global_config import env_bool, get_cookie_from_file
from bili_downloader.config.settings import Settings
from bili_downloader.core.bangumi_downloader import (
    QUALITY_OPTIONS,
    BangumiDownloader,
)
from bili_downloader.exceptions import (
    APIError,
    BiliDownloaderError,
    DownloadError,
    MergeError,
)
from bili_downloader.utils.logger import logger

app = typer.Typer()
console = Console()


# 移除了get_cookie函数，使用全局配置模块提供的get_cookie_from_file函数
def get_user_input(settings: Settings):
    """获取用户输入的 URL、下载目录、清晰度选项、清理选项和下载器类型。"""
    # 从用户获取输入，如果直接回车则使用默认值
    # URL默认值优先级：环境变量 > 配置文件历史记录 > 空字符串
    default_url = os.environ.get("DOWNLOAD__DEFAULT_URL")
    # 如果环境变量未设置或为空，则使用配置文件中的历史URL
    if not default_url:
        default_url = settings.history.last_url
    video_url = Prompt.ask(
        "Enter Video URL",
        default=default_url if default_url else "",
    )

    # 下载目录默认值优先级：环境变量 > 配置文件历史记录 > 标准默认目录
    default_directory = os.environ.get(
        "DOWNLOAD__DEFAULT_DIRECTORY", settings.history.last_directory
    )
    if not default_directory:
        default_directory = str(Path.home() / "Downloads" / "bili_downloader")
    record_url = Prompt.ask(
        "Enter Download Directory",
        default=default_directory,
    )

    keyword = Prompt.ask(
        "Enter keyword to filter episodes (leave empty for all episodes)",
        default="",
    )

    doclean = Confirm.ask(
        "Clean .flv/.ogg files after merging?",
        default=settings.download.cleanup_after_merge,
    )

    # 显示清晰度选项并获取用户选择
    # 清晰度默认值优先级：环境变量 > 配置文件默认值
    default_quality = int(
        os.environ.get("DOWNLOAD__DEFAULT_QUALITY", settings.download.default_quality)
    )
    console.print("\nAvailable quality options:")
    for qn, desc in QUALITY_OPTIONS.items():
        default_mark = " (default)" if qn == default_quality else ""
        console.print(f"  {qn}: {desc}{default_mark}")

    while True:
        quality_choice = Prompt.ask(
            "\nSelect quality (enter number)",
            default=str(default_quality),
        ).strip()
        if not quality_choice:
            selected_qn = default_quality
            break
        try:
            selected_qn = int(quality_choice)
            if selected_qn in QUALITY_OPTIONS:
                break
            else:
                console.print(
                    "Please enter a valid quality number from the options above."
                )
        except ValueError:
            console.print("Please enter a valid number.")

    # 显示下载器选项并获取用户选择
    # 下载器默认值优先级：环境变量 > 配置文件默认值
    default_downloader = os.environ.get(
        "DOWNLOAD__DEFAULT_DOWNLOADER", settings.download.default_downloader
    )
    available_downloaders = ["axel", "aria2"]
    console.print("Available downloaders:")
    for i, dl in enumerate(available_downloaders, 1):
        default_mark = " (default)" if dl == default_downloader else ""
        console.print(f"  {i}. {dl}{default_mark}")

    while True:
        downloader_choice = Prompt.ask(
            f"Select downloader (1-{len(available_downloaders)})",
            default="1" if default_downloader == "axel" else "2",
        ).strip()
        if not downloader_choice:
            downloader_type = default_downloader
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

    return video_url, record_url, selected_qn, doclean, downloader_type, keyword


@app.command()
def download(
    url: str = typer.Option("", "--url", "-u", help="视频URL下载"),
    directory: str = typer.Option("", "--directory", "-d", help="下载目录"),
    threads: int = typer.Option(16, "--threads", "-t", help="下载线程数"),
    quality: int = typer.Option(0, "--quality", "-q", help="视频清晰度"),
    cleanup: bool = typer.Option(False, "--cleanup", "-c", help="合并后清理"),
    downloader: str = typer.Option(
        "", "--downloader", "-D", help="使用的下载器 (axel 或 aria2)"
    ),
    keyword: str = typer.Option(
        "",
        "--keyword",
        "-k",
        help="关键字过滤剧集 (仅下载标题包含此关键字的剧集)",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="启用详细日志"),
):
    """
    下载哔哩哔哩番剧

    从指定的 URL 下载哔哩哔哩番剧视频，并保存到指定目录。
    """
    try:
        # Load settings from global config
        from bili_downloader.cli.global_config import _global_cli_args

        settings = _global_cli_args.get("settings")
        if not settings:
            # Fallback to loading from file if global config is not available
            settings = Settings.load_from_file()

        # Cookie
        cookie_dict = get_cookie_from_file()
        # 如果cookie_dict为空，提示用户输入
        if not cookie_dict:
            cookie_str = Prompt.ask("请粘贴您的Bilibili cookie").strip()
            if not cookie_str:
                console.print("[red]错误: 需要Cookie。[/red]")
                raise typer.Exit(code=1)
            # 将cookie字符串转换为字典
            cookie_dict = dict(
                item.split("=", 1) for item in cookie_str.split("; ") if "=" in item
            )

        cookie = BangumiDownloader({}, {}).convert_cookie_to_dict(
            "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
        )

        # Input
        # 检查是否通过命令行提供了必要的参数 (url 和 directory)
        # 如果提供了，则使用命令行参数，并从 settings 或 defaults 获取其他参数的值
        # 否则，进入交互式模式
        if url:
            # 使用命令行参数
            video_url = url
            default_directory = os.environ.get(
                "DOWNLOAD__DEFAULT_DIRECTORY", settings.history.last_directory
            )
            directory = directory if directory else default_directory
            # 对于其他参数，如果命令行未提供，则使用配置文件或默认值
            default_quality = os.environ.get(
                "DOWNLOAD__DEFAULT_QUALITY", settings.download.default_quality
            )
            default_cleanup = env_bool(
                "DOWNLOAD__CLEANUP_AFTER_MERGE", settings.download.cleanup_after_merge
            )
            raw = os.getenv("DOWNLOAD__DEFAULT_THREADS")
            default_threads = (
                int(raw) if raw is not None else settings.download.default_threads
            )
            default_downloader = os.environ.get(
                "DOWNLOAD__DEFAULT_DOWNLOADER", settings.download.default_downloader
            )
            selected_qn = quality if quality > 0 else int(default_quality)
            doclean = cleanup if cleanup else default_cleanup
            downloader_type = downloader if downloader else default_downloader
            filter_keyword = keyword  # keyword 的默认值是空字符串，符合预期
            threads = default_threads if default_threads else threads
        else:
            # 否则交互式获取用户输入
            (
                video_url,
                directory,
                selected_qn,
                doclean,
                downloader_type,
                filter_keyword,
            ) = get_user_input(settings)

        # 保存历史记录
        if video_url:
            settings.history.last_url = video_url
        if directory:
            settings.history.last_directory = directory
        settings.save_to_file()

        console.print(
            f"正在从 {video_url} 下载到 {directory}，清晰度 {selected_qn}，使用 {downloader_type}"
        )
        if filter_keyword:
            console.print(f"使用关键字过滤剧集: {filter_keyword}")

        # Create downloader instance
        downloader_instance = BangumiDownloader(cookie)
        console.print("开始获取详细信息")
        # 使用默认头部下载
        info = downloader_instance.get_detailed_info_from_url(
            video_url, settings.network.headers
        )
        # print(f"\nget detail info: {info}")
        # Pass the selected quality to the download function
        merged_files = downloader_instance.download_all_from_info_with_quality(
            info,
            directory,
            selected_qn,
            doclean,
            settings.network.headers,
            downloader_type,
            filter_keyword,  # Pass keyword filter
            threads,
        )
        console.print(f"\nDownload completed. Merged {len(merged_files)} files:")
        for file in merged_files:
            console.print(f"  - {file}")

    except KeyboardInterrupt:
        console.print("\n[yellow]下载被用户中断。[/yellow]")
        logger.info("Download interrupted by user")
        raise typer.Exit(code=1)
    except APIError as e:
        console.print(f"[red]API错误: {e}[/red]")
        logger.error("API Error", error=str(e))
        raise typer.Exit(code=1)
    except DownloadError as e:
        console.print(f"[red]下载错误: {e}[/red]")
        logger.error("Download Error", error=str(e))
        raise typer.Exit(code=1)
    except MergeError as e:
        console.print(f"[red]合并错误: {e}[/red]")
        logger.error("Merge Error", error=str(e))
        raise typer.Exit(code=1)
    except BiliDownloaderError as e:
        console.print(f"[red]BiliDownloader错误: {e}[/red]")
        logger.error("BiliDownloader Error", error=str(e))
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]发生未预期的错误: {e}[/red]")
        logger.error("An unexpected error occurred", error=str(e))
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
