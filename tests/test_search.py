from unittest.mock import MagicMock, patch

from bili_downloader.core.search import BilibiliSearch


def test_get_mixin_key():
    """测试获取mixin key功能"""
    searcher = BilibiliSearch()

    # 测试正常情况
    orig = "7cd084941338484aae1ad9425b84077c" + "4932caff0ff746eab6f01bf08b70ac45"
    expected = "ea1db124af3c7062474693fa704f4ff8"
    result = searcher._get_mixin_key(orig)
    assert result == expected
    assert len(result) == 32


def test_enc_wbi():
    """测试WBI签名功能"""
    searcher = BilibiliSearch()

    # 测试参数签名
    params = {"foo": "114", "bar": "514", "baz": 1919810}
    img_key = "7cd084941338484aae1ad9425b84077c"
    sub_key = "4932caff0ff746eab6f01bf08b70ac45"

    signed_params = searcher._enc_wbi(params, img_key, sub_key)

    # 检查必要的字段是否存在
    assert "wts" in signed_params
    assert "w_rid" in signed_params
    assert signed_params["foo"] == "114"
    assert signed_params["bar"] == "514"
    assert signed_params["baz"] == "1919810"


@patch("bili_downloader.core.search.requests.Session")
def test_get_wbi_keys(mock_session):
    """测试获取WBI密钥功能"""
    # 模拟响应
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": {
            "wbi_img": {
                "img_url": "https://i0.hdslb.com/bfs/wbi/7cd084941338484aae1ad9425b84077c.png",
                "sub_url": "https://i0.hdslb.com/bfs/wbi/4932caff0ff746eab6f01bf08b70ac45.png",
            }
        }
    }
    mock_response.raise_for_status.return_value = None

    mock_session_instance = MagicMock()
    mock_session_instance.get.return_value = mock_response
    mock_session.return_value = mock_session_instance

    searcher = BilibiliSearch()
    img_key, sub_key = searcher._get_wbi_keys()

    assert img_key == "7cd084941338484aae1ad9425b84077c"
    assert sub_key == "4932caff0ff746eab6f01bf08b70ac45"


@patch("bili_downloader.core.search.requests.Session")
def test_search_all(mock_session):
    """测试综合搜索功能"""
    # 模拟响应
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 0,
        "message": "0",
        "data": {"result": []},
    }
    mock_response.raise_for_status.return_value = None

    mock_session_instance = MagicMock()
    mock_session_instance.get.return_value = mock_response
    mock_session.return_value = mock_session_instance

    # 模拟_get_wbi_keys方法
    with patch.object(
        BilibiliSearch, "_get_wbi_keys", return_value=("img_key", "sub_key")
    ):
        searcher = BilibiliSearch()
        result = searcher.search_all("测试关键词")

        assert result["code"] == 0
        assert result["message"] == "0"


@patch("bili_downloader.core.search.requests.Session")
def test_search_by_type(mock_session):
    """测试分类搜索功能"""
    # 模拟响应
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 0,
        "message": "0",
        "data": {"result": []},
    }
    mock_response.raise_for_status.return_value = None

    mock_session_instance = MagicMock()
    mock_session_instance.get.return_value = mock_response
    mock_session.return_value = mock_session_instance

    # 模拟_get_wbi_keys方法
    with patch.object(
        BilibiliSearch, "_get_wbi_keys", return_value=("img_key", "sub_key")
    ):
        searcher = BilibiliSearch()
        result = searcher.search_by_type("video", "测试关键词")

        assert result["code"] == 0
        assert result["message"] == "0"


def test_search_bangumi():
    """测试番剧搜索功能"""
    with patch.object(BilibiliSearch, "search_by_type") as mock_search_by_type:
        mock_search_by_type.return_value = {"code": 0, "data": {}}

        searcher = BilibiliSearch()
        result = searcher.search_bangumi("测试番剧")

        mock_search_by_type.assert_called_once_with("media_bangumi", "测试番剧", page=1)
        assert result["code"] == 0


def test_search_video():
    """测试视频搜索功能"""
    with patch.object(BilibiliSearch, "search_by_type") as mock_search_by_type:
        mock_search_by_type.return_value = {"code": 0, "data": {}}

        searcher = BilibiliSearch()
        result = searcher.search_video("测试视频", order="click", page=2)

        mock_search_by_type.assert_called_once_with(
            "video", "测试视频", order="click", page=2
        )
        assert result["code"] == 0


def test_search_user():
    """测试用户搜索功能"""
    with patch.object(BilibiliSearch, "search_by_type") as mock_search_by_type:
        mock_search_by_type.return_value = {"code": 0, "data": {}}

        searcher = BilibiliSearch()
        result = searcher.search_user("测试用户", page=3)

        mock_search_by_type.assert_called_once_with("bili_user", "测试用户", page=3)
        assert result["code"] == 0
