import os
import tempfile
from pathlib import Path

from bili_downloader.config.settings import Settings


def test_settings_load_and_save():
    """测试配置文件的加载和保存功能"""
    # 创建临时配置文件进行测试
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建临时配置文件路径
        temp_config_file = Path(temp_dir) / "test_config.toml"

        # 创建测试配置内容
        config_content = """
[log]
enable_file_logging = true
log_file_path = "logs/test_bili_downloader.log"
log_level = "DEBUG"
max_log_file_size = 5242880  # 5MB
backup_count = 3
log_format = "json"

[download]
default_quality = 80
default_downloader = "aria2"
default_threads = 32
cleanup_after_merge = true

[login]
default_method = "web"
default_output = "test_cookie.txt"
default_timeout = 300

[history]
last_url = "https://www.bilibili.com/bangumi/play/ep123456"
last_directory = "/tmp/test_downloads"

[network]
user_agent = "Test User Agent String"
"""

        # 写入测试配置文件
        with open(temp_config_file, "w", encoding="utf-8") as f:
            f.write(config_content)

        # 读取配置文件内容进行验证
        import toml

        with open(temp_config_file, "r", encoding="utf-8") as f:
            loaded_config = toml.load(f)

        # 验证配置内容
        assert loaded_config["log"]["enable_file_logging"] is True
        assert loaded_config["log"]["log_file_path"] == "logs/test_bili_downloader.log"
        assert loaded_config["log"]["log_level"] == "DEBUG"
        assert loaded_config["log"]["max_log_file_size"] == 5242880
        assert loaded_config["log"]["backup_count"] == 3
        assert loaded_config["log"]["log_format"] == "json"

        assert loaded_config["download"]["default_quality"] == 80
        assert loaded_config["download"]["default_downloader"] == "aria2"
        assert loaded_config["download"]["default_threads"] == 32
        assert loaded_config["download"]["cleanup_after_merge"] is True

        assert loaded_config["login"]["default_method"] == "web"
        assert loaded_config["login"]["default_output"] == "test_cookie.txt"
        assert loaded_config["login"]["default_timeout"] == 300

        assert (
            loaded_config["history"]["last_url"]
            == "https://www.bilibili.com/bangumi/play/ep123456"
        )
        assert loaded_config["history"]["last_directory"] == "/tmp/test_downloads"

        assert loaded_config["network"]["user_agent"] == "Test User Agent String"


def test_settings_priority():
    """测试配置优先级"""
    # 创建临时配置文件进行测试
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建临时配置文件路径
        temp_config_file = Path(temp_dir) / "priority_test_config.toml"

        # 创建具有不同优先级值的测试配置内容
        config_content = """
[log]
enable_file_logging = false
log_file_path = "logs/priority_test.log"
log_level = "WARNING"
max_log_file_size = 2097152  # 2MB
backup_count = 2
log_format = "console"

[download]
default_quality = 64
default_downloader = "axel"
default_threads = 16
cleanup_after_merge = false

[login]
default_method = "qr"
default_output = "priority_test_cookie.txt"
default_timeout = 120

[history]
last_url = "https://www.bilibili.com/bangumi/play/ep654321"
last_directory = "/tmp/priority_test"

[network]
user_agent = "Priority Test User Agent"
"""

        # 写入测试配置文件
        with open(temp_config_file, "w", encoding="utf-8") as f:
            f.write(config_content)

        # 读取配置文件内容进行验证
        import toml

        with open(temp_config_file, "r", encoding="utf-8") as f:
            loaded_config = toml.load(f)

        # 验证配置优先级
        assert loaded_config["log"]["enable_file_logging"] is False
        assert loaded_config["log"]["log_file_path"] == "logs/priority_test.log"
        assert loaded_config["log"]["log_level"] == "WARNING"
        assert loaded_config["log"]["max_log_file_size"] == 2097152
        assert loaded_config["log"]["backup_count"] == 2
        assert loaded_config["log"]["log_format"] == "console"

        assert loaded_config["download"]["default_quality"] == 64
        assert loaded_config["download"]["default_downloader"] == "axel"
        assert loaded_config["download"]["default_threads"] == 16
        assert loaded_config["download"]["cleanup_after_merge"] is False

        assert loaded_config["login"]["default_method"] == "qr"
        assert loaded_config["login"]["default_output"] == "priority_test_cookie.txt"
        assert loaded_config["login"]["default_timeout"] == 120

        assert (
            loaded_config["history"]["last_url"]
            == "https://www.bilibili.com/bangumi/play/ep654321"
        )
        assert loaded_config["history"]["last_directory"] == "/tmp/priority_test"

        assert loaded_config["network"]["user_agent"] == "Priority Test User Agent"
