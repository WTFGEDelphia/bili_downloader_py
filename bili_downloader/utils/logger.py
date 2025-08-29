import structlog
import sys
import os

def configure_logger(verbose: bool = False):
    """
    配置 structlog 日志记录器。
    
    Args:
        verbose (bool): 是否启用详细日志。
    """
    # 配置根 logger
    level = "DEBUG" if verbose else "INFO"
    
    # 使用更简单的配置
    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # 配置基本的日志记录
    import logging
    logging.basicConfig(
        level=level,
        format="%(message)s",
        stream=sys.stderr,
    )

# 创建全局 logger 实例
logger = structlog.get_logger()