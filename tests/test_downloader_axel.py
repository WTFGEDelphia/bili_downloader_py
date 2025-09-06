from unittest.mock import MagicMock, patch

from bili_downloader.core.downloader_axel import DownloaderAxel


@patch("bili_downloader.core.downloader_axel.find_executable")
def test_downloader_axel_init(mock_find_executable):
    """测试DownloaderAxel初始化"""
    mock_find_executable.return_value = "/usr/bin/axel"

    downloader = DownloaderAxel("http://example.com/test.mp4", 8, "/tmp/test.mp4")

    assert downloader.url == "http://example.com/test.mp4"
    assert downloader.num == 8
    assert downloader.dest == "/tmp/test.mp4"
    assert downloader.max_retry == 3


@patch("bili_downloader.core.downloader_axel.find_executable")
def test_downloader_axel_init_with_custom_headers(mock_find_executable):
    """测试DownloaderAxel初始化时自定义头部"""
    mock_find_executable.return_value = "/usr/bin/axel"

    headers = {"User-Agent": "test", "Referer": "http://test.com"}
    downloader = DownloaderAxel(
        "http://example.com/test.mp4", 8, "/tmp/test.mp4", headers
    )

    assert downloader.header == headers


@patch("bili_downloader.core.downloader_axel.find_executable")
@patch("bili_downloader.core.downloader_axel.axel_path", "/usr/bin/axel")
@patch("os.makedirs")
@patch("subprocess.run")
def test_downloader_axel_run_success(
    mock_subprocess_run, mock_makedirs, mock_find_executable
):
    """测试DownloaderAxel成功运行"""
    mock_find_executable.return_value = "/usr/bin/axel"

    # 模拟成功的子进程运行
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""
    mock_subprocess_run.return_value = mock_result

    downloader = DownloaderAxel("http://example.com/test.mp4", 8, "/tmp/test.mp4")
    result = downloader.run()

    assert result is True
    mock_subprocess_run.assert_called_once()


@patch("bili_downloader.core.downloader_axel.find_executable")
@patch("bili_downloader.core.downloader_axel.axel_path", None)
def test_downloader_axel_run_without_executable(mock_find_executable):
    """测试DownloaderAxel在没有可执行文件时运行"""
    mock_find_executable.return_value = None

    downloader = DownloaderAxel("http://example.com/test.mp4", 8, "/tmp/test.mp4")
    result = downloader.run()

    assert result is False


@patch("bili_downloader.core.downloader_axel.find_executable")
@patch("bili_downloader.core.downloader_axel.axel_path", "/usr/bin/axel")
@patch("os.makedirs")
@patch("subprocess.run")
def test_downloader_axel_run_failure(
    mock_subprocess_run, mock_makedirs, mock_find_executable
):
    """测试DownloaderAxel运行失败"""
    mock_find_executable.return_value = "/usr/bin/axel"

    # 模拟失败的子进程运行
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Download failed"
    mock_subprocess_run.return_value = mock_result

    downloader = DownloaderAxel("http://example.com/test.mp4", 8, "/tmp/test.mp4")
    result = downloader.run()

    assert result is False


@patch("bili_downloader.core.downloader_axel.find_executable")
@patch("bili_downloader.core.downloader_axel.axel_path", "/usr/bin/axel")
@patch("os.makedirs")
@patch("subprocess.run")
def test_downloader_axel_run_with_retry(
    mock_subprocess_run, mock_makedirs, mock_find_executable
):
    """测试DownloaderAxel重试机制"""
    mock_find_executable.return_value = "/usr/bin/axel"

    # 模拟前两次失败，第三次成功
    mock_result1 = MagicMock()
    mock_result1.returncode = 1
    mock_result1.stdout = ""
    mock_result1.stderr = "Download failed"

    mock_result2 = MagicMock()
    mock_result2.returncode = 1
    mock_result2.stdout = ""
    mock_result2.stderr = "Download failed"

    mock_result3 = MagicMock()
    mock_result3.returncode = 0
    mock_result3.stdout = ""
    mock_result3.stderr = ""

    mock_subprocess_run.side_effect = [mock_result1, mock_result2, mock_result3]

    downloader = DownloaderAxel(
        "http://example.com/test.mp4", 8, "/tmp/test.mp4", max_retry=3
    )
    result = downloader.run()

    assert result is True
    assert mock_subprocess_run.call_count == 3
