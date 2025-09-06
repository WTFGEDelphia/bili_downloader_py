from bili_downloader.config.settings import Settings


def test_settings():
    """测试配置加载"""
    settings = Settings()

    # 测试默认值
    assert settings.download.default_quality == 127
    assert settings.download.default_downloader == "axel"
    assert settings.download.default_threads == 64
    assert settings.download.cleanup_after_merge is True

    assert (
        settings.network.user_agent
        == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
    )
