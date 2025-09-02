import pytest

from bili_downloader.config.settings import Settings


def test_settings():
    """测试配置加载"""
    settings = Settings()

    # 测试默认值
    assert settings.download.default_quality == 112
    assert settings.download.default_downloader == "axel"
    assert settings.download.default_threads == 16
    assert settings.download.cleanup_after_merge is False

    assert (
        settings.network.user_agent
        == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
