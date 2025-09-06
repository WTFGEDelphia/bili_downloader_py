#!/usr/bin/env python3

import typer

from bili_downloader.cli.cmd_download import download
from bili_downloader.cli.cmd_login import login

app = typer.Typer()

# Register subcommands
app.command()(download)
app.command()(login)


# Add global options
@app.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    """
    Bilibili Bangumi Downloader - 下载哔哩哔哩番剧视频
    """
    # 这里可以添加全局配置逻辑
    pass


if __name__ == "__main__":
    app()
