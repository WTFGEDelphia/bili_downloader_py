import os
from unittest.mock import patch

from bili_downloader.cli.global_config import (
    env_bool,
    get_cookie_from_file,
    setup_global_config,
)


def test_setup_global_config():
    """测试全局配置设置"""
    # 测试不带详细日志的配置
    result = setup_global_config()
    assert "settings" in result
    assert "verbose" in result
    assert result["verbose"] is False


def test_setup_global_config_with_verbose():
    """测试带详细日志的全局配置设置"""
    result = setup_global_config(verbose=True)
    assert "settings" in result
    assert "verbose" in result
    assert result["verbose"] is True


@patch("os.path.exists")
@patch("builtins.open")
def test_get_cookie_from_file_found(mock_open, mock_exists):
    """测试从文件获取Cookie-文件存在"""
    mock_exists.return_value = True
    mock_open.return_value.__enter__.return_value.read.return_value = (
        "SESSDATA=test_sessdata; bili_jct=test_jct"
    )

    cookie = get_cookie_from_file()

    assert "SESSDATA" in cookie
    assert cookie["SESSDATA"] == "test_sessdata"


@patch("os.path.exists")
def test_get_cookie_from_file_not_found(mock_exists):
    """测试从文件获取Cookie-文件不存在"""
    mock_exists.return_value = False

    cookie = get_cookie_from_file()

    assert cookie == {}


def test_env_bool_true_values():
    """测试env_bool函数-真值"""
    # 测试各种真值情况
    with patch.dict(os.environ, {"TEST_VAR": "1"}):
        assert env_bool("TEST_VAR") is True

    with patch.dict(os.environ, {"TEST_VAR": "true"}):
        assert env_bool("TEST_VAR") is True

    with patch.dict(os.environ, {"TEST_VAR": "yes"}):
        assert env_bool("TEST_VAR") is True

    with patch.dict(os.environ, {"TEST_VAR": "on"}):
        assert env_bool("TEST_VAR") is True


def test_env_bool_false_values():
    """测试env_bool函数-假值"""
    # 测试各种假值情况
    with patch.dict(os.environ, {"TEST_VAR": "0"}):
        assert env_bool("TEST_VAR") is False

    with patch.dict(os.environ, {"TEST_VAR": "false"}):
        assert env_bool("TEST_VAR") is False

    with patch.dict(os.environ, {"TEST_VAR": "no"}):
        assert env_bool("TEST_VAR") is False

    with patch.dict(os.environ, {"TEST_VAR": "off"}):
        assert env_bool("TEST_VAR") is False

    with patch.dict(os.environ, {"TEST_VAR": ""}):
        assert env_bool("TEST_VAR") is False


def test_env_bool_default_value():
    """测试env_bool函数-默认值"""
    # 测试不存在的环境变量使用默认值
    # 删除测试变量（如果存在）
    if "TEST_NON_EXISTENT_VAR" in os.environ:
        del os.environ["TEST_NON_EXISTENT_VAR"]

    # 确保使用默认值
    assert env_bool("TEST_NON_EXISTENT_VAR", default=True) is True
    assert env_bool("TEST_NON_EXISTENT_VAR", default=False) is False


def test_env_bool_other_values():
    """测试env_bool函数-其他值"""
    # 测试其他值按Python的bool语义处理
    with patch.dict(os.environ, {"TEST_VAR": "other"}):
        assert env_bool("TEST_VAR") is True
