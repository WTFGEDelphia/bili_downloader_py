"""
Bilibili搜索命令模块
"""

import json

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from bili_downloader.cli.global_config import get_cookie_from_file
from bili_downloader.config.settings import Settings
from bili_downloader.core.search import BilibiliSearch
from bili_downloader.exceptions import BiliDownloaderError
from bili_downloader.utils.logger import logger

app = typer.Typer()
console = Console()

def get_media_score(media_score: dict) -> float:
    """获取媒体评分"""
    if not media_score or isinstance(media_score, dict):
        return float(media_score.get("score", 0))
    return 0.0

def _display_search_results(results: dict, search_type: str = "all"):
    """
    显示搜索结果
    """
    if search_type == "all":
        _display_all_search_results(results)
    else:
        _display_type_search_results(results, search_type)


def _display_all_search_results(results: dict):
    """
    显示综合搜索结果
    """
    data = results.get("data", {})
    result_list = data.get("result", [])

    if not result_list:
        console.print("[yellow]未找到搜索结果。[/yellow]")
        logger.debug("未找到搜索结果。")
        return

    # 显示不同类型的搜索结果
    for result_item in result_list:
        result_type = result_item.get("result_type", "")
        data_list = result_item.get("data", [])

        if not data_list:
            continue

        table = Table(
            title=f"{result_type.upper()} Results",
            show_header=True,
            header_style="bold magenta",
        )

        # 根据不同类型设置表格列
        if result_type == "video":
            table.add_column("Title", style="cyan", no_wrap=False)
            table.add_column("Author", style="green")
            table.add_column("Play Count", style="yellow")
            table.add_column("Duration", style="blue")

            for item in data_list[:10]:  # 只显示前10个结果
                title = (
                    item.get("title", "")
                    .replace('<em class="keyword">', "")
                    .replace("</em>", "")
                )
                author = item.get("author", "")
                play = item.get("play", 0)
                duration = item.get("duration", "")

                # 格式化播放量
                if play >= 10000:
                    play_str = f"{play/10000:.1f}万"
                else:
                    play_str = str(play)

                table.add_row(title, author, play_str, duration)
        elif result_type == "bili_user":
            table.add_column("Username", style="cyan")
            table.add_column("Sign", style="green")
            table.add_column("Fans", style="yellow")
            table.add_column("Videos", style="blue")

            for item in data_list[:10]:  # 只显示前10个结果
                username = item.get("uname", "")
                sign = item.get("usign", "")
                fans = item.get("fans", 0)
                videos = item.get("videos", 0)

                # 格式化粉丝数
                if fans >= 10000:
                    fans_str = f"{fans/10000:.1f}万"
                else:
                    fans_str = str(fans)

                table.add_row(
                    username,
                    sign[:30] + "..." if len(sign) > 30 else sign,
                    fans_str,
                    str(videos),
                )

        elif result_type == "media_bangumi":
            table.add_column("番名", style="cyan", max_width=40, overflow="fold")
            table.add_column("分类", style="green", max_width=9, overflow="fold")
            table.add_column("配音/演员表", style="yellow", max_width=16, overflow="fold")
            table.add_column("评分", style="bold yellow", justify="right")
            table.add_column("更新进度", style="blue", justify="center")
            table.add_column("封面", style="blue", justify="center", max_width=12, overflow="fold")
            table.add_column("pgc_season_id", style="dim", justify="center", width=15)
            table.add_column("media_id", style="dim", justify="center", width=10)
            table.add_column("season_id", style="dim", justify="center", width=10)

            for item in data_list[:10]:
                title = (
                    item.get("title", "")
                    .replace('<em class="keyword">', "")
                    .replace("</em>", "")
                )
                styles = (item.get("styles", []))
                cv = item.get("cv", "")
                media_score = item.get("media_score", {})
                score = get_media_score(media_score)
                index_show = item.get("index_show", "")
                cover = item.get("cover", "")
                pgc_season_id = item.get("pgc_season_id", 0)
                media_id = item.get("media_id", 0)
                season_id = item.get("season_id", 0)

                # 为 score 添加条件样式
                score_str = str(score)
                if score and float(score) >= 8.0:
                    score_str = f"[bold green]{score_str}[/]"
                elif score and float(score) >= 6.0:
                    score_str = f"[bold yellow]{score_str}[/]"
                elif score:
                    score_str = f"[bold red]{score_str}[/]"

                table.add_row(
                    title,
                    styles,
                    cv,
                    score_str,  # 使用格式化后的 score
                    index_show,
                    cover,
                    str(pgc_season_id),
                    str(media_id),
                    str(season_id),
                )

        console.print(table)
        console.print("")
        # else:
        #     # 其他类型显示基本信息
        #     table.add_column("Info", style="cyan")
        #     for item in data_list[:1]:  # 只显示前5个结果
        #         table.add_row(json.dumps(item, ensure_ascii=False, indent=2))
        # console.print(table)
        # console.print("")


def _display_type_search_results(results: dict, search_type: str):
    """
    显示分类搜索结果
    """
    data = results.get("data", {})
    result_list = data.get("result", [])

    if not result_list:
        console.print("[yellow]未找到搜索结果。[/yellow]")
        logger.debug("未找到搜索结果。")
        return

    table = Table(
        title=f"{search_type.upper()} Search Results",
        show_header=True,
        header_style="bold magenta",
    )

    # 根据搜索类型设置表格列
    if search_type == "video":
        table.add_column("Title", style="cyan", no_wrap=False)
        table.add_column("Author", style="green")
        table.add_column("Play Count", style="yellow")
        table.add_column("Duration", style="blue")
        table.add_column("URL", style="dim")

        for item in result_list[:10]:  # 只显示前10个结果
            title = (
                item.get("title", "")
                .replace('<em class="keyword">', "")
                .replace("</em>", "")
            )
            author = item.get("author", "")
            play = item.get("play", 0)
            duration = item.get("duration", "")
            bvid = item.get("bvid", "")
            url = f"https://www.bilibili.com/video/{bvid}" if bvid else ""

            # 格式化播放量
            if play >= 10000:
                play_str = f"{play/10000:.1f}万"
            else:
                play_str = str(play)

            table.add_row(title, author, play_str, duration, url)

    elif search_type == "media_bangumi":
        table.add_column("番名", style="cyan", max_width=40, overflow="fold")
        table.add_column("分类", style="green", max_width=9, overflow="fold")
        table.add_column("配音/演员表", style="yellow", max_width=16, overflow="fold")
        table.add_column("评分", style="bold yellow", justify="right")
        table.add_column("更新进度", style="blue", justify="center")
        table.add_column("封面", style="blue", justify="center", max_width=12, overflow="fold")
        table.add_column("pgc_season_id", style="dim", justify="center", width=15)
        table.add_column("media_id", style="dim", justify="center", width=10)
        table.add_column("season_id", style="dim", justify="center", width=10)

        for item in result_list[:10]:
            title = (
                item.get("title", "")
                .replace('<em class="keyword">', "")
                .replace("</em>", "")
            )
            styles = (item.get("styles", []))
            cv = item.get("cv", "")
            media_score = item.get("media_score", {})
            score = get_media_score(media_score)
            index_show = item.get("index_show", "")
            cover = item.get("cover", "")
            pgc_season_id = item.get("pgc_season_id", 0)
            media_id = item.get("media_id", 0)
            season_id = item.get("season_id", 0)

            # 为 score 添加条件样式
            score_str = str(score)
            if score and float(score) >= 8.0:
                score_str = f"[bold green]{score_str}[/]"
            elif score and float(score) >= 6.0:
                score_str = f"[bold yellow]{score_str}[/]"
            elif score:
                score_str = f"[bold red]{score_str}[/]"

            table.add_row(
                title,
                styles,
                cv,
                score_str,  # 使用格式化后的 score
                index_show,
                cover,
                str(pgc_season_id),
                str(media_id),
                str(season_id),
            )

    elif search_type == "bili_user":
        table.add_column("Username", style="cyan")
        table.add_column("Sign", style="green")
        table.add_column("Fans", style="yellow")
        table.add_column("Videos", style="blue")
        table.add_column("URL", style="dim")

        for item in result_list[:10]:
            username = item.get("uname", "")
            sign = item.get("usign", "")
            fans = item.get("fans", 0)
            videos = item.get("videos", 0)
            mid = item.get("mid", "")
            url = f"https://space.bilibili.com/{mid}" if mid else ""

            # 格式化粉丝数
            if fans >= 10000:
                fans_str = f"{fans/10000:.1f}万"
            else:
                fans_str = str(fans)

            table.add_row(
                username,
                sign[:30] + "..." if len(sign) > 30 else sign,
                fans_str,
                str(videos),
                url,
            )
    # else:
    #     # 其他类型显示基本信息
    #     table.add_column("Info", style="cyan")
    #     for item in result_list[:10]:  # 只显示前10个结果
    #         table.add_row(json.dumps(item, ensure_ascii=False, indent=2))

    console.print(table)

    # 记录表格数据到日志
    logger.debug(f"显示 {search_type.upper()} 搜索结果:")
    # 只记录前3个结果的简要信息，避免日志文件过大
    for item in result_list[:3]:
        title = item.get("title", "")
        logger.debug(f"  标题: {title}")


@app.command()
def search(
    keyword: str = typer.Option("", "--keyword", "-k", help="搜索关键词"),
    search_type: str = typer.Option(
        "all", "--type", "-t", help="搜索类型: all, video, bangumi, user"
    ),
    order: str = typer.Option("totalrank", "--order", "-o", help="视频搜索的排序方式"),
    page: int = typer.Option(1, "--page", "-p", help="页码"),
    save: bool = typer.Option(False, "--save", "-s", help="保存搜索结果到文件"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="启用详细日志"),
):
    """
    搜索Bilibili内容

    支持多种搜索类型：
    - all: 综合搜索（默认）
    - video: 视频搜索
    - bangumi: 番剧搜索
    - user: 用户搜索
    """
    try:
        # Load settings from global config
        from bili_downloader.cli.global_config import _global_cli_args

        settings = _global_cli_args.get("settings")
        if not settings:
            # Fallback to loading from file if global config is not available
            settings = Settings.load_from_file()

        # 获取Cookie
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

        cookie = cookie_dict

        # 如果没有提供关键词，则交互式获取
        if not keyword:
            keyword = Prompt.ask("输入搜索关键词").strip()
            if not keyword:
                console.print("[red]错误: 搜索关键词是必需的。[/red]")
                raise typer.Exit(code=1)

        # 创建搜索实例
        searcher = BilibiliSearch(cookie)

        # 根据搜索类型执行搜索
        console.print(f"[green]正在搜索:[/green] {keyword}")

        if search_type == "all":
            results = searcher.search_all(keyword)
        elif search_type == "video":
            results = searcher.search_video(keyword, order=order, page=page)
        elif search_type == "bangumi":
            search_type = "media_bangumi"
            results = searcher.search_bangumi(keyword, page=page)
        elif search_type == "user":
            results = searcher.search_user(keyword, page=page)
        else:
            console.print(f"[red]错误: 不支持的搜索类型: {search_type}[/red]")
            raise typer.Exit(code=1)

        # 显示搜索结果
        _display_search_results(results, search_type)

        # 保存搜索结果到文件
        if save:
            output_file = f"search_results_{keyword}_{search_type}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            console.print(f"[green]搜索结果已保存到:[/green] {output_file}")

        logger.info("Search completed", keyword=keyword, type=search_type)

    except KeyboardInterrupt:
        console.print("\n[yellow]搜索被用户中断。[/yellow]")
        logger.info("Search interrupted by user")
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
