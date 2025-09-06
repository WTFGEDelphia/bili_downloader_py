import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path

import structlog


class CustomTimeStamper(structlog.processors.TimeStamper):
    def __call__(self, logger, method_name, event_dict):
        # 调用父类方法获取时间戳（UTC或本地时间）
        event_dict = super().__call__(logger, method_name, event_dict)

        # 解析并替换格式
        timestamp = event_dict["timestamp"]
        if isinstance(timestamp, str) and "T" in timestamp:
            # 处理ISO格式（如UTC时间）
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if self.utc:
                dt = dt.astimezone()  # 转换为本地时间
            formatted = (
                dt.strftime("%Y-%m-%d %H:%M:%S") + f",{dt.microsecond // 1000:03d}"
            )
            event_dict["timestamp"] = formatted
        return event_dict


def _configure_processors(log_format: str = "json"):
    """根据指定格式配置处理器"""
    processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        # structlog.processors.TimeStamper(utc=True),
        CustomTimeStamper(fmt="iso", utc=True),  # 父类生成ISO时间，子类格式化
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # 根据格式添加相应的渲染器
    if log_format.lower() == "json":
        processors.append(structlog.processors.JSONRenderer(ensure_ascii=False))
    elif log_format.lower() == "keyvalue":
        processors.append(
            structlog.processors.KeyValueRenderer(
                key_order=["timestamp", "level", "logger", "event"]
            )
        )
    elif log_format.lower() == "simple":
        processors.append(structlog.dev.ConsoleRenderer(colors=False))
    else:  # console format (default)
        processors.append(structlog.dev.ConsoleRenderer())

    return processors


def configure_logger(verbose: bool = False, log_settings=None):
    """
    配置 structlog 日志记录器。

    Args:
        verbose (bool): 是否启用详细日志。
        log_settings: 日志设置对象
    """
    # 配置根 logger
    level = "DEBUG" if verbose else "INFO"

    # 获取日志格式设置，默认为json
    log_format = log_settings.log_format if log_settings else "json"

    # 获取根日志记录器
    root_logger = logging.getLogger()

    # 清除之前的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 如果提供了日志设置并且启用了文件日志，则配置文件处理器
    if log_settings and log_settings.enable_file_logging:
        # 创建日志目录（如果不存在）
        log_file_path = Path(log_settings.log_file_path)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # 配置文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=log_settings.max_log_file_size,
            backupCount=log_settings.backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, log_settings.log_level.upper()))

        # 文件处理器始终使用 '%(message)s' 格式化器，以确保与 structlog 处理器兼容
        formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # 配置控制台处理器
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)

    # 为控制台处理器设置格式化器（简单格式）
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)

    root_logger.addHandler(console_handler)
    root_logger.setLevel(
        getattr(logging, log_settings.log_level.upper()) if log_settings else level
    )

    # 使用配置的处理器
    structlog.configure(
        processors=_configure_processors(log_format),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# 创建全局 logger 实例
logger = structlog.get_logger()
