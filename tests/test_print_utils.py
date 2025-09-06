import pytest

from bili_downloader.utils.print_utils import (
    print_error,
    print_info,
    print_message,
    print_success,
    print_warning,
)


def test_print_info():
    """测试打印信息消息"""
    # 由于print_utils使用了rich的Console，我们主要测试函数是否能正常调用
    try:
        print_info("Test info message")
        assert True  # 如果没有异常则测试通过
    except Exception:
        pytest.fail("console.print raised an exception")


def test_print_warning():
    """测试打印警告消息"""
    try:
        print_warning("Test warning message")
        assert True  # 如果没有异常则测试通过
    except Exception:
        pytest.fail("print_warning raised an exception")


def test_print_error():
    """测试打印错误消息"""
    try:
        print_error("Test error message")
        assert True  # 如果没有异常则测试通过
    except Exception:
        pytest.fail("print_error raised an exception")


def test_print_success():
    """测试打印成功消息"""
    try:
        print_success("Test success message")
        assert True  # 如果没有异常则测试通过
    except Exception:
        pytest.fail("print_success raised an exception")


def test_print_message():
    """测试打印普通消息"""
    try:
        print_message("Test message")
        assert True  # 如果没有异常则测试通过
    except Exception:
        pytest.fail("print_message raised an exception")


def test_print_message_with_style():
    """测试打印带样式的普通消息"""
    try:
        print_message("Test message", style="bold red")
        assert True  # 如果没有异常则测试通过
    except Exception:
        pytest.fail("print_message with style raised an exception")
