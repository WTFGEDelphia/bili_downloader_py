"""
统一的日志打印模块
"""

import datetime
import inspect

from rich.console import Console

# 创建全局Console实例
console = Console()


def _format_message(level: str, message: str) -> str:
    """
    格式化消息，使其与 structlog 的 simple 格式一致

    Args:
        level: 日志级别
        message: 日志消息

    Returns:
        格式化后的消息字符串
    """
    # 获取当前时间戳
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    # 获取调用栈信息以确定 logger name
    frame = inspect.currentframe().f_back.f_back
    module_name = frame.f_globals["__name__"] if frame else "unknown"
    # 返回格式化的消息
    return f"{timestamp} - {module_name} - {level.upper()} - {message}"


def print_info(message: str) -> None:
    """
    打印信息消息

    Args:
        message: 要打印的消息
    """
    formatted_message = _format_message("INFO", message)
    console.print(formatted_message)


def print_warning(message: str) -> None:
    """
    打印警告消息

    Args:
        message: 要打印的消息
    """
    formatted_message = _format_message("WARNING", message)
    console.print(f"[yellow]{formatted_message}[/yellow]")


def print_error(message: str) -> None:
    """
    打印错误消息

    Args:
        message: 要打印的消息
    """
    formatted_message = _format_message("ERROR", message)
    console.print(f"[red]{formatted_message}[/red]")


def print_success(message: str) -> None:
    """
    打印成功消息

    Args:
        message: 要打印的消息
    """
    formatted_message = _format_message("INFO", message)
    console.print(f"[green]{formatted_message}[/green]")


def print_message(message: str, style: str = "") -> None:
    """
    打印普通消息

    Args:
        message: 要打印的消息
        style: 样式字符串
    """
    if style:
        console.print(message, style=style)
    else:
        console.print(message)
