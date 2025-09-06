from unittest.mock import MagicMock, patch

from bili_downloader.core.vamerger import VAMerger


@patch("bili_downloader.core.vamerger.find_executable")
def test_vamerger_init(mock_find_executable):
    """测试VAMerger初始化"""
    mock_find_executable.return_value = "/usr/bin/ffmpeg"

    merger = VAMerger("/tmp/audio.mp3", "/tmp/video.mp4", "/tmp/output.mp4")

    assert merger.audio == "/tmp/audio.mp3"
    assert merger.video == "/tmp/video.mp4"
    assert merger.output == "/tmp/output.mp4"


@patch("bili_downloader.core.vamerger.find_executable")
@patch("bili_downloader.core.vamerger.ffmpeg_path", "/usr/bin/ffmpeg")
@patch("os.makedirs")
@patch("subprocess.run")
def test_vamerger_run_success(mock_subprocess_run, mock_makedirs, mock_find_executable):
    """测试VAMerger成功运行"""
    mock_find_executable.return_value = "/usr/bin/ffmpeg"

    # 模拟成功的子进程运行
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""
    mock_subprocess_run.return_value = mock_result

    merger = VAMerger("/tmp/audio.mp3", "/tmp/video.mp4", "/tmp/output.mp4")
    result = merger.run()

    assert result is True
    mock_subprocess_run.assert_called_once()


@patch("bili_downloader.core.vamerger.find_executable")
def test_vamerger_run_without_executable(mock_find_executable):
    """测试VAMerger在没有可执行文件时运行"""
    mock_find_executable.return_value = None

    # 直接修改模块级别的ffmpeg_path变量
    import bili_downloader.core.vamerger as vamerger_module

    original_ffmpeg_path = vamerger_module.ffmpeg_path
    vamerger_module.ffmpeg_path = None

    try:
        merger = VAMerger("/tmp/audio.mp3", "/tmp/video.mp4", "/tmp/output.mp4")
        result = merger.run()

        assert result is False
    finally:
        # 恢复原始值
        vamerger_module.ffmpeg_path = original_ffmpeg_path


@patch("bili_downloader.core.vamerger.find_executable")
@patch("bili_downloader.core.vamerger.ffmpeg_path", "/usr/bin/ffmpeg")
@patch("os.makedirs")
@patch("subprocess.run")
def test_vamerger_run_failure(mock_subprocess_run, mock_makedirs, mock_find_executable):
    """测试VAMerger运行失败"""
    mock_find_executable.return_value = "/usr/bin/ffmpeg"

    # 模拟失败的子进程运行
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Merge failed"
    mock_subprocess_run.return_value = mock_result

    merger = VAMerger("/tmp/audio.mp3", "/tmp/video.mp4", "/tmp/output.mp4")
    result = merger.run()

    assert result is False


@patch("bili_downloader.core.vamerger.find_executable")
@patch("bili_downloader.core.vamerger.ffmpeg_path", "/usr/bin/ffmpeg")
@patch("os.makedirs")
@patch("subprocess.run")
def test_vamerger_run_subprocess_error(
    mock_subprocess_run, mock_makedirs, mock_find_executable
):
    """测试VAMerger运行时出现子进程错误"""
    mock_find_executable.return_value = "/usr/bin/ffmpeg"

    # 模拟子进程错误
    mock_subprocess_run.side_effect = Exception("Subprocess error")

    merger = VAMerger("/tmp/audio.mp3", "/tmp/video.mp4", "/tmp/output.mp4")
    result = merger.run()

    assert result is False
