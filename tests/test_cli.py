from typer.testing import CliRunner

from bili_downloader.cli.main import app

runner = CliRunner()


def test_download_command():
    """测试下载命令"""
    # 测试帮助信息
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "下载哔哩哔哩番剧" in result.stdout
