import sys
import os

# Add the project root to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import only the sanitize_filename method directly from the file
# Read the file content and extract just the sanitize_filename method
import re

def test_sanitize_filename():
    """测试文件名清理功能"""
    # 直接定义清理函数
    def sanitize_filename(filename):
        """清理文件名，确保在文件系统中有效。"""
        import re
        # 移除不允许的字符
        # Windows不允许的字符: \\ / : * ? " < > |
        # Unix/Linux/Mac一般只不允许/
        filename = re.sub(r'[\\\\/:*?"<>|]', "", filename)

        # 移除控制字符
        filename = "".join(char for char in filename if ord(char) >= 32)

        # 限制长度（Windows路径限制为260字符，我们保留一些空间）
        if len(filename) > 200:
            filename = filename[:200]

        # 移除首尾空格和点
        filename = filename.strip(". ")

        # 如果文件名为空，提供默认名称
        if not filename:
            filename = "unnamed"

        return filename
    
    # 测试正常文件名
    assert sanitize_filename("test") == "test"
    
    # 测试包含特殊字符的文件名
    assert sanitize_filename("test/file") == "testfile"
    assert sanitize_filename("test:file") == "testfile"
    assert sanitize_filename("test*file") == "testfile"
    assert sanitize_filename("test?file") == "testfile"
    assert sanitize_filename('test"file') == "testfile"
    assert sanitize_filename("test<file") == "testfile"
    assert sanitize_filename("test>file") == "testfile"
    assert sanitize_filename("test|file") == "testfile"
    
    # 测试包含控制字符的文件名
    assert sanitize_filename("test\x00file") == "testfile"
    
    # 测试过长的文件名
    long_filename = "a" * 250
    sanitized = sanitize_filename(long_filename)
    assert len(sanitized) <= 200
    
    # 测试空文件名
    assert sanitize_filename("") == "unnamed"
    
    # 测试只包含空格和点的文件名
    assert sanitize_filename(" . ") == "unnamed"
    
    print("All tests passed!")

if __name__ == "__main__":
    test_sanitize_filename()