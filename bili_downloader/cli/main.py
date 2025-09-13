#!/usr/bin/env python3

import typer

from bili_downloader.cli.cmd_download import download
from bili_downloader.cli.cmd_login import login
from bili_downloader.cli.cmd_search import search
from bili_downloader.cli.global_config import _global_cli_args, setup_global_config

app = typer.Typer()

# 注册子命令
app.command()(download)
app.command()(login)
app.command()(search)


# 添加全局选项
@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="启用详细日志"),
    log_to_file: bool = typer.Option(
        False, "--log-to-file", "-l", help="将日志输出到文件"
    ),
    log_format: str = typer.Option(
        "simple", "--log-format", "-f", help="日志格式 (json, console, keyvalue, simple)"
    ),
):
    """
    Bilibili Bangumi Downloader - 下载哔哩哔哩番剧视频
    """
    # 设置全局配置
    global_config = setup_global_config(verbose, log_format)
    # 将全局配置存储在全局变量中，供子命令使用
    _global_cli_args["settings"] = global_config["settings"]
    # 将verbose参数也存储在全局变量中，供子命令使用
    _global_cli_args["verbose"] = verbose

    # 如果启用了文件日志，则更新设置并重新配置logger
    if log_to_file:
        # 直接使用已加载的设置，而不是重新加载
        settings = _global_cli_args["settings"]
        settings.log.enable_file_logging = True
        settings.log.log_format = log_format
        settings.save_to_file()
        # 重新配置logger以启用文件日志
        from bili_downloader.utils.logger import configure_logger

        configure_logger(verbose, settings.log)


if __name__ == "__main__":
    app()
