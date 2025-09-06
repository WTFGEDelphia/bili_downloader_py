from unittest.mock import MagicMock, patch

from bili_downloader.core.downloader_aria2 import DownloaderAria2


@patch("bili_downloader.core.downloader_aria2.find_executable")
def test_downloader_aria2_init(mock_find_executable):
    """测试DownloaderAria2初始化"""
    mock_find_executable.return_value = "/usr/bin/aria2c"

    downloader = DownloaderAria2("http://example.com/test.mp4", 8, "/tmp/test.mp4")

    assert downloader.url == "http://example.com/test.mp4"
    assert downloader.num == 8
    assert downloader.dest == "/tmp/test.mp4"
    assert downloader.max_retry == 3


@patch("bili_downloader.core.downloader_aria2.find_executable")
def test_downloader_aria2_init_with_high_thread_count(mock_find_executable):
    """测试DownloaderAria2初始化时线程数超过16的情况"""
    mock_find_executable.return_value = "/usr/bin/aria2c"

    downloader = DownloaderAria2("http://example.com/test.mp4", 20, "/tmp/test.mp4")

    # 线程数应该被限制为16
    assert downloader.num == 16


@patch("bili_downloader.core.downloader_aria2.find_executable")
def test_downloader_aria2_init_with_custom_headers(mock_find_executable):
    """测试DownloaderAria2初始化时自定义头部"""
    mock_find_executable.return_value = "/usr/bin/aria2c"

    headers = {"User-Agent": "test", "Referer": "http://test.com"}
    downloader = DownloaderAria2(
        "http://example.com/test.mp4", 8, "/tmp/test.mp4", headers
    )

    assert downloader.header == headers


@patch("bili_downloader.core.downloader_aria2.find_executable")
@patch("bili_downloader.core.downloader_aria2.aria2c_path", "/usr/bin/aria2c")
@patch("os.makedirs")
@patch("subprocess.run")
def test_downloader_aria2_run_success(
    mock_subprocess_run, mock_makedirs, mock_find_executable
):
    """测试DownloaderAria2成功运行"""
    mock_find_executable.return_value = "/usr/bin/aria2c"

    # 模拟成功的子进程运行
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""
    mock_subprocess_run.return_value = mock_result

    downloader = DownloaderAria2("http://example.com/test.mp4", 8, "/tmp/test.mp4")
    result = downloader.run()

    assert result is True
    mock_subprocess_run.assert_called_once()


@patch("bili_downloader.core.downloader_aria2.find_executable")
@patch("bili_downloader.core.downloader_aria2.aria2c_path", None)
def test_downloader_aria2_run_without_executable(mock_find_executable):
    """测试DownloaderAria2在没有可执行文件时运行"""
    mock_find_executable.return_value = None

    downloader = DownloaderAria2("http://example.com/test.mp4", 8, "/tmp/test.mp4")
    result = downloader.run()

    assert result is False


@patch("bili_downloader.core.downloader_aria2.find_executable")
@patch("bili_downloader.core.downloader_aria2.aria2c_path", "/usr/bin/aria2c")
@patch("os.makedirs")
@patch("subprocess.run")
def test_downloader_aria2_run_failure(
    mock_subprocess_run, mock_makedirs, mock_find_executable
):
    """测试DownloaderAria2运行失败"""
    mock_find_executable.return_value = "/usr/bin/aria2c"

    # 模拟失败的子进程运行
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Download failed"
    mock_subprocess_run.return_value = mock_result

    downloader = DownloaderAria2("http://example.com/test.mp4", 8, "/tmp/test.mp4")
    result = downloader.run()

    assert result is False
