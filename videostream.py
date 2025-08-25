import json
import os
import re
from urllib.parse import urlparse

import requests

from downloader_aria2 import DownloaderAria2
from downloader_axel import DownloaderAxel

# Default quality and format parameters
DEFAULT_QN = 112
DEFAULT_FNVAL = 0b111111010000

# Default downloader type
DEFAULT_DOWNLOADER = "axel"  # or "aria2"


def convert_cookie_to_dict(cookie):
    """将 Cookie 字符串转换为字典。"""
    if not cookie:
        return {}
    try:
        # Split by "; " or just ";" to handle different formats
        # Then split by the first "=" to separate key and value
        cookies = {}
        # First, try splitting by "; "
        cookie_parts = cookie.split("; ")
        # If that doesn't work, try splitting by ";"
        if len(cookie_parts) <= 1:
            cookie_parts = cookie.split(";")

        for part in cookie_parts:
            part = part.strip()  # Remove leading/trailing whitespace
            if not part:
                continue
            # Split by the first "=" to handle values that might contain "="
            if "=" in part:
                key, value = part.split("=", 1)
                # For certain cookie keys that might have special characters,
                # we need to ensure they are properly formatted for HTTP headers
                # Some characters in cookie values might cause issues with HTTP headers
                cookies[key] = value
        return cookies
    except Exception as e:
        # Handle case where cookie string is malformed
        print(f"Warning: Cookie string might be malformed: {e}")
        return {}


def check_result_code(result):
    """检查 API 返回的业务逻辑错误码。"""
    if result.get("code") != 0:
        print(f"API Error: {result}")
        # Instead of sys.exit, raise an exception for better error handling
        raise Exception(f"API returned error code {result.get('code')}")


def get_bangumi_info(media_id, headers=None, cookie=None):
    """根据 media_id 获取番剧基础信息。"""
    if headers is None:
        headers = {}
    # Make a copy of the cookie dict to avoid modifying the original
    cookie_dict = cookie.copy() if cookie and isinstance(cookie, dict) else {}

    params = {"media_id": media_id}
    try:
        response = requests.get(
            "https://api.bilibili.com/pgc/review/user",
            params=params,
            headers=headers,
            cookies=cookie_dict,
            timeout=10,
        )
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        result = response.json()
        check_result_code(result)
        return result["result"]["media"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching bangumi info for media_id {media_id}: {e}")
        raise
    except json.JSONDecodeError:
        print(f"Error decoding JSON response for media_id {media_id}")
        raise
    except KeyError:
        print(f"Unexpected response structure for media_id {media_id}")
        raise


def get_detailed_bangumi_info_from_season_id(season_id, headers=None, cookie=None):
    """根据 season_id 获取番剧详细信息。"""
    if headers is None:
        headers = {}
    # Make a copy of the cookie dict to avoid modifying the original
    cookie_dict = cookie.copy() if cookie and isinstance(cookie, dict) else {}

    params = {"season_id": season_id}
    try:
        response = requests.get(
            "https://api.bilibili.com/pgc/view/web/season",
            params=params,
            headers=headers,
            cookies=cookie_dict,
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        check_result_code(result)
        return result["result"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching detailed bangumi info for season_id {season_id}: {e}")
        raise
    except json.JSONDecodeError:
        print(f"Error decoding JSON response for season_id {season_id}")
        raise
    except KeyError:
        print(f"Unexpected response structure for season_id {season_id}")
        raise


def get_detailed_bangumi_info_from_ep_id(ep_id, headers=None, cookie=None):
    """根据 ep_id 获取番剧详细信息。"""
    if headers is None:
        headers = {}
    # Make a copy of the cookie dict to avoid modifying the original
    cookie_dict = cookie.copy() if cookie and isinstance(cookie, dict) else {}

    params = {"ep_id": ep_id}
    try:
        response = requests.get(
            "https://api.bilibili.com/pgc/view/web/season",
            params=params,
            headers=headers,
            cookies=cookie_dict,
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        check_result_code(result)
        return result["result"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching detailed bangumi info for ep_id {ep_id}: {e}")
        raise
    except json.JSONDecodeError:
        print(f"Error decoding JSON response for ep_id {ep_id}")
        raise
    except KeyError:
        print(f"Unexpected response structure for ep_id {ep_id}")
        raise


def get_numbers_in_str(string):
    """从字符串中提取数字。"""
    # Using regex is more robust and efficient
    match = re.search(r"\d+", string)
    return match.group() if match else ""


def get_detailed_info_from_url(url, headers=None, cookie=None):
    """根据 URL 解析并获取番剧详细信息。"""
    if headers is None:
        headers = {}

    url = url.rstrip("/")
    parsed_url = urlparse(url)

    if not parsed_url.netloc or not parsed_url.scheme:
        raise ValueError("Invalid URL provided.")

    path = parsed_url.path

    if "/bangumi/media/" in path:
        # Extract media ID from path like /bangumi/media/md191
        media_id = get_numbers_in_str(path)
        if not media_id:
            raise ValueError("Could not extract media ID from the URL.")
        print(f"media_id = {media_id}")
        season_id = get_bangumi_info(media_id, headers, cookie)["season_id"]
        return get_detailed_bangumi_info_from_season_id(season_id, headers, cookie)
    else:
        # Assume it's an episode URL
        ep_id = get_numbers_in_str(path)
        if not ep_id:
            raise ValueError("Could not extract episode ID from the URL.")
        print(f"ep_id = {ep_id}")
        return get_detailed_bangumi_info_from_ep_id(ep_id, headers, cookie)


def get_bangumi_download_info(cookie, aid, cid, headers=None):
    """获取特定视频的下载信息。"""
    if headers is None:
        headers = {}

    # Ensure referer is present
    headers = headers.copy()
    headers.setdefault("referer", "https://www.bilibili.com")

    # Make a copy of the cookie dict to avoid modifying the original
    cookie_dict = cookie.copy() if isinstance(cookie, dict) else {}

    params = {"aid": aid, "cid": cid, "qn": DEFAULT_QN, "fnval": DEFAULT_FNVAL}
    try:
        response = requests.get(
            "https://api.bilibili.com/pgc/player/web/playurl",
            headers=headers,
            params=params,
            cookies=cookie_dict,
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        check_result_code(result)
        return result["result"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching download info for aid={aid}, cid={cid}: {e}")
        raise
    except json.JSONDecodeError:
        print(f"Error decoding JSON response for aid={aid}, cid={cid}")
        raise
    except KeyError:
        print(f"Unexpected response structure for aid={aid}, cid={cid}")
        raise


def sanitize_filename(filename):
    """清理文件名，确保在文件系统中有效。"""
    # 移除不允许的字符
    # Windows不允许的字符: \ / : * ? " < > |
    # Unix/Linux/Mac一般只不允许/
    filename = re.sub(r'[\\/:*?"<>|]', "", filename)

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


def get_bangumi_downloads(cookie, aid, cid, headers=None):
    """获取视频和音频的下载链接列表。"""
    if headers is None:
        headers = {}
    try:
        downinfo = get_bangumi_download_info(cookie, aid, cid, headers)["dash"]
        audios = downinfo["audio"]
        videos = downinfo["video"]

        # Select the first audio and video stream
        if not audios or not videos:
            raise Exception("No audio or video streams found in the response.")

        # Return lists of URLs
        return ([audios[0]["base_url"]], [videos[0]["base_url"]])
    except (KeyError, IndexError) as e:
        print(f"Error parsing download URLs for aid={aid}, cid={cid}: {e}")
        raise


def download_bangumi(
    url, dest, headers=None, num=16, refurl="", downloader_type=DEFAULT_DOWNLOADER
):
    """下载单个视频或音频文件。"""
    if headers is None:
        headers = {}

    # Ensure referer is present and properly formatted
    headers = headers.copy()
    referer_value = refurl or "https://www.bilibili.com"
    # Ensure the referer value is a string and doesn't contain problematic characters
    if isinstance(referer_value, str):
        # Remove any control characters that might cause issues
        referer_value = "".join(char for char in referer_value if ord(char) >= 32)
    headers.setdefault("referer", referer_value)

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    # Select downloader based on type
    if downloader_type.lower() == "aria2":
        downloader = DownloaderAria2(url, num, dest, header=headers)
    else:
        downloader = DownloaderAxel(url, num, dest, header=headers)

    if not downloader.run():
        print(f"\x1b[031mDownload failed: {url} -> {dest}\x1b[0m")
        return False  # Indicate failure
    return True  # Indicate success
