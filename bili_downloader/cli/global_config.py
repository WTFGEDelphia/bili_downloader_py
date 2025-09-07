"""
全局配置管理模块
"""

import os
from pathlib import Path
from typing import Any

import requests
from rich.console import Console

from bili_downloader.config.settings import Settings
from bili_downloader.utils.logger import configure_logger, logger

console = Console()

# 全局变量存储CLI参数
_global_cli_args = {}


def setup_global_config(
    verbose: bool = False, log_format: str = None
) -> dict[str, Any]:
    """
    设置全局配置

    Args:
        verbose: 是否启用详细日志
        log_format: 日志格式 (json, console, keyvalue, simple)

    Returns:
        包含全局配置的字典
    """
    # 加载设置
    settings = Settings.load_from_file()

    # 如果CLI中指定了日志格式，则覆盖配置文件中的设置
    if log_format:
        settings.log.log_format = log_format

    # 配置日志
    configure_logger(verbose, settings.log)

    logger.info("全局配置设置完成")

    return {"settings": settings, "verbose": verbose}


def get_cookie_from_file() -> dict[str, str]:
    """
    从文件读取Cookie

    Returns:
        Cookie字典
    """
    cookie = {}
    # 定义多个可能的cookie文件路径
    possible_paths = [
        # Docker环境中的挂载路径
        os.path.join(Path.home(), ".config", "bili-downloader", "cookie.txt"),
        # 原始路径
        os.path.join(os.getcwd(), "cookie.txt"),
    ]

    cookie_file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            cookie_file_path = path
            break

    if cookie_file_path:
        try:
            with open(cookie_file_path) as f:
                cookie_str = f.read().strip()
            console.print(f"Cookie已从 {cookie_file_path} 加载")

            # 将cookie字符串转换为字典
            if cookie_str:
                cookie = dict(
                    item.split("=", 1) for item in cookie_str.split("; ") if "=" in item
                )
        except Exception as e:
            console.print(f"无法从 {cookie_file_path} 读取Cookie: {e}")
    else:
        console.print("在以下位置未找到Cookie文件:")
        for path in possible_paths:
            console.print(f"  - {path}")

    return cookie


def is_cookie_valid(cookie: dict[str, str]) -> bool:
    """
    验证B站Cookie是否有效

    Args:
        cookie: Cookie字典

    Returns:
        Cookie是否有效
    """
    try:
        # 加载全局设置以获取User-Agent
        settings = Settings.load_from_file()
        
        # 将cookie字典转换为cookie字符串
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookie.items()])
        
        # 创建会话并设置cookie
        session = requests.Session()
        session.headers.update({
            "User-Agent": settings.network.user_agent,
            "Referer": "https://www.bilibili.com/"
        })
        session.cookies.update(cookie)
        
        # 请求用户导航信息API
        resp = session.get("https://api.bilibili.com/x/web-interface/nav")
        resp.raise_for_status()
        json_content = resp.json()
        
        # 检查返回码
        # code为0表示已登录，-101表示未登录
        if json_content.get("code") == 0:
            return True
        else:
            return False
    except Exception as e:
        logger.error("验证Cookie时出错", error=str(e))
        return False


def env_bool(key: str, default: bool = False) -> bool:
    """
    把环境变量 key 解析为 bool；未设置或空串返回 default。

    Args:
        key: 环境变量键名
        default: 默认值

    Returns:
        解析后的布尔值
    """
    val = os.environ.get(key, "").strip().lower()
    if val in {"1", "true", "yes", "on"}:
        return True
    if val in {"0", "false", "no", "off", ""}:
        return default  # 当值为空时返回默认值
    # 如果值既不是上面任何一项，就按 Python 的 bool 语义兜底
    return bool(val)