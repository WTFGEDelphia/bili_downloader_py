import pytest

from bili_downloader.core.bangumi_downloader import BangumiDownloader


def test_sanitize_filename():
    """测试文件名清理功能"""
    downloader = BangumiDownloader({}, {})

    # 测试正常文件名
    assert downloader.sanitize_filename("test") == "test"

    # 测试包含特殊字符的文件名
    assert downloader.sanitize_filename("test/file") == "testfile"
    assert downloader.sanitize_filename("test:file") == "testfile"
    assert downloader.sanitize_filename("test*file") == "testfile"
    assert downloader.sanitize_filename("test?file") == "testfile"
    assert downloader.sanitize_filename('test"file') == "testfile"
    assert downloader.sanitize_filename("test<file") == "testfile"
    assert downloader.sanitize_filename("test>file") == "testfile"
    assert downloader.sanitize_filename("test|file") == "testfile"

    # 测试包含控制字符的文件名
    assert downloader.sanitize_filename("test\x00file") == "testfile"

    # 测试过长的文件名
    long_filename = "a" * 250
    sanitized = downloader.sanitize_filename(long_filename)
    assert len(sanitized) <= 200

    # 测试空文件名
    assert downloader.sanitize_filename("") == "unnamed"

    # 测试只包含空格和点的文件名
    assert downloader.sanitize_filename(" . ") == "unnamed"
