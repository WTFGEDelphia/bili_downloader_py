import unittest
from unittest.mock import patch, Mock

from bili_downloader.cli.global_config import is_cookie_valid


class TestCookieValidation(unittest.TestCase):
    
    @patch('requests.Session')
    def test_valid_cookie(self, mock_session_class):
        # 创建mock响应
        mock_response = Mock()
        mock_response.json.return_value = {"code": 0}
        mock_response.raise_for_status.return_value = None
        
        # 设置mock session
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # 测试有效的cookie
        cookie = {"SESSDATA": "valid_sessdata", "bili_jct": "valid_bili_jct"}
        result = is_cookie_valid(cookie)
        
        self.assertTrue(result)
        mock_session.get.assert_called_once_with("https://api.bilibili.com/x/web-interface/nav")
    
    @patch('requests.Session')
    def test_invalid_cookie(self, mock_session_class):
        # 创建mock响应
        mock_response = Mock()
        mock_response.json.return_value = {"code": -101}  # 未登录
        mock_response.raise_for_status.return_value = None
        
        # 设置mock session
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # 测试无效的cookie
        cookie = {"SESSDATA": "invalid_sessdata", "bili_jct": "invalid_bili_jct"}
        result = is_cookie_valid(cookie)
        
        self.assertFalse(result)
    
    @patch('requests.Session')
    def test_network_error(self, mock_session_class):
        # 模拟网络错误
        mock_session = Mock()
        mock_session.get.side_effect = Exception("Network error")
        mock_session_class.return_value = mock_session
        
        # 测试网络错误
        cookie = {"SESSDATA": "some_sessdata", "bili_jct": "some_bili_jct"}
        result = is_cookie_valid(cookie)
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()