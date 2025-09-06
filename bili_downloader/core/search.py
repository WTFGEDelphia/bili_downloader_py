import time
import urllib.parse
from functools import reduce
from hashlib import md5

import requests

from bili_downloader.utils.logger import logger

# WBI签名相关常量
MIXIN_KEY_ENC_TAB = [
    46,
    47,
    18,
    2,
    53,
    8,
    23,
    32,
    15,
    50,
    10,
    31,
    58,
    3,
    45,
    35,
    27,
    43,
    5,
    49,
    33,
    9,
    42,
    19,
    29,
    28,
    14,
    39,
    12,
    38,
    41,
    13,
    37,
    48,
    7,
    16,
    24,
    55,
    40,
    61,
    26,
    17,
    0,
    1,
    60,
    51,
    30,
    4,
    22,
    25,
    54,
    21,
    56,
    59,
    6,
    63,
    57,
    62,
    11,
    36,
    20,
    34,
    44,
    52,
]


class BilibiliSearch:
    """Bilibili搜索功能类"""

    def __init__(self, cookie: dict | None = None):
        """初始化搜索器

        Args:
            cookie: Bilibili登录cookie字典
        """
        self.cookie = cookie or {}
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": "https://www.bilibili.com/",
            }
        )
        if self.cookie:
            self.session.cookies.update(self.cookie)

    def _get_mixin_key(self, orig: str) -> str:
        """对img_key和sub_key进行字符顺序打乱编码"""
        # 确保orig字符串足够长，避免索引越界
        if len(orig) < 64:
            # 如果长度不够，用原字符串重复填充到至少64个字符
            orig = (orig * ((64 // len(orig)) + 1))[:64]
        return reduce(lambda s, i: s + orig[i], MIXIN_KEY_ENC_TAB, "")[:32]

    def _enc_wbi(self, params: dict, img_key: str, sub_key: str) -> dict:
        """为请求参数进行wbi签名"""
        mixin_key = self._get_mixin_key(img_key + sub_key)
        curr_time = round(time.time())
        params["wts"] = curr_time  # 添加wts字段
        params = dict(sorted(params.items()))  # 按照key重排参数

        # 过滤value中的"!'()*"字符
        params = {
            k: "".join(filter(lambda chr: chr not in "!'()*", str(v)))
            for k, v in params.items()
        }

        query = urllib.parse.urlencode(params)  # 序列化参数
        wbi_sign = md5((query + mixin_key).encode()).hexdigest()  # 计算w_rid
        params["w_rid"] = wbi_sign
        return params

    def _get_wbi_keys(self) -> tuple[str, str]:
        """获取最新的img_key和sub_key"""
        try:
            # 先尝试获取buvid3 cookie
            self.session.get("https://www.bilibili.com/")

            # 获取WBI密钥
            resp = self.session.get("https://api.bilibili.com/x/web-interface/nav")
            resp.raise_for_status()
            json_content = resp.json()

            img_url: str = json_content["data"]["wbi_img"]["img_url"]
            sub_url: str = json_content["data"]["wbi_img"]["sub_url"]
            img_key = img_url.rsplit("/", 1)[1].split(".")[0]
            sub_key = sub_url.rsplit("/", 1)[1].split(".")[0]
            return img_key, sub_key
        except Exception as e:
            logger.error("Failed to get WBI keys", error=str(e))
            raise Exception(f"获取WBI密钥失败: {e}")

    def search_all(self, keyword: str) -> dict:
        """综合搜索（web端）

        Args:
            keyword: 搜索关键词

        Returns:
            搜索结果的JSON数据
        """
        try:
            # 获取WBI签名密钥
            img_key, sub_key = self._get_wbi_keys()

            # 构造请求参数
            params = {"keyword": keyword}

            # 进行WBI签名
            signed_params = self._enc_wbi(params, img_key, sub_key)

            # 发送请求
            response = self.session.get(
                "https://api.bilibili.com/x/web-interface/wbi/search/all/v2",
                params=signed_params,
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()

            if result.get("code") != 0:
                logger.error(
                    "Search API returned error",
                    code=result.get("code"),
                    message=result.get("message"),
                )
                raise Exception(f"搜索失败: {result.get('message')}")

            return result
        except Exception as e:
            logger.error("综合搜索失败", error=str(e))
            raise Exception(f"综合搜索失败: {e}")

    def search_by_type(
        self,
        search_type: str,
        keyword: str,
        order: str = "totalrank",
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """分类搜索（web端）

        Args:
            search_type: 搜索类型
                - video: 视频
                - media_bangumi: 番剧
                - media_ft: 影视
                - live: 直播间及主播
                - live_room: 直播间
                - live_user: 主播
                - article: 专栏
                - topic: 话题
                - bili_user: 用户
                - photo: 相簿
            keyword: 搜索关键词
            order: 排序方式
                - 综合排序: totalrank
                - 最多点击: click
                - 最新发布: pubdate
                - 最多弹幕: dm
                - 最多收藏: stow
                - 最多评论: scores
                - 最多喜欢: attention (仅用于专栏)
            page: 页码
            page_size: 每页条数

        Returns:
            搜索结果的JSON数据
        """
        try:
            # 获取WBI签名密钥
            img_key, sub_key = self._get_wbi_keys()

            # 构造请求参数
            params = {
                "search_type": search_type,
                "keyword": keyword,
                "order": order,
                "page": page,
                "page_size": page_size,
            }

            # 进行WBI签名
            signed_params = self._enc_wbi(params, img_key, sub_key)

            # 发送请求
            response = self.session.get(
                "https://api.bilibili.com/x/web-interface/wbi/search/type",
                params=signed_params,
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()

            if result.get("code") != 0:
                logger.error(
                    "分类搜索接口返回错误",
                    code=result.get("code"),
                    message=result.get("message"),
                )
                raise Exception(f"分类搜索失败: {result.get('message')}")

            return result
        except Exception as e:
            logger.error("分类搜索失败", error=str(e))
            raise Exception(f"分类搜索失败: {e}")

    def search_bangumi(self, keyword: str, page: int = 1) -> dict:
        """搜索番剧

        Args:
            keyword: 搜索关键词
            page: 页码

        Returns:
            搜索结果的JSON数据
        """
        return self.search_by_type("media_bangumi", keyword, page=page)

    def search_video(
        self, keyword: str, order: str = "totalrank", page: int = 1
    ) -> dict:
        """搜索视频

        Args:
            keyword: 搜索关键词
            order: 排序方式
            page: 页码

        Returns:
            搜索结果的JSON数据
        """
        return self.search_by_type("video", keyword, order=order, page=page)

    def search_user(self, keyword: str, page: int = 1) -> dict:
        """搜索用户

        Args:
            keyword: 搜索关键词
            page: 页码

        Returns:
            搜索结果的JSON数据
        """
        return self.search_by_type("bili_user", keyword, page=page)
