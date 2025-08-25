import json
import os
import re
from urllib.parse import urlparse

import requests

from downloader_aria2 import DownloaderAria2
from downloader_axel import DownloaderAxel
from vamerger import VAMerger

# Default quality and format parameters
DEFAULT_QN = 112
DEFAULT_FNVAL = 0b111111010000

# 清晰度选项
QUALITY_OPTIONS = {
    6: "240P 极速 (仅 MP4, 移动端 HTML5 场景)",
    16: "360P 流畅 (默认最低档)",
    32: "480P 清晰 (无需登录)",
    64: "720P 高清 (需登录, Web 端默认值)",
    74: "720P60 高帧率 (需登录)",
    80: "1080P 高清 (需登录, TV/APP 默认值)",
    100: "智能修复 (需大会员)",
    112: "1080P+ 高码率 (需大会员)",
    116: "1080P60 高帧率 (需大会员)",
    120: "4K 超清 (需大会员)",
    125: "HDR 真彩 (需大会员)",
    126: "杜比视界 (需大会员)",
    127: "8K 超高清 (需大会员)",
}

# Default downloader type
DEFAULT_DOWNLOADER = "aria2"  # or "axel"


class BangumiDownloader:
    """Bilibili 番剧下载器类"""

    def __init__(self, cookie, headers=None):
        """初始化下载器"""
        self.cookie = cookie
        self.headers = headers if headers is not None else {}

    def convert_cookie_to_dict(self, cookie):
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

    def check_result_code(self, result):
        """检查 API 返回的业务逻辑错误码。"""
        if result.get("code") != 0:
            print(f"API Error: {result}")
            # Instead of sys.exit, raise an exception for better error handling
            raise Exception(f"API returned error code {result.get('code')}")

    def get_bangumi_info(self, media_id, headers=None):
        """根据 media_id 获取番剧基础信息。"""
        if headers is None:
            headers = {}
        # Make a copy of the cookie dict to avoid modifying the original
        cookie_dict = (
            self.cookie.copy() if self.cookie and isinstance(self.cookie, dict) else {}
        )

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
            self.check_result_code(result)
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

    def get_detailed_bangumi_info_from_season_id(self, season_id, headers=None):
        """根据 season_id 获取番剧详细信息。"""
        if headers is None:
            headers = {}
        # Make a copy of the cookie dict to avoid modifying the original
        cookie_dict = (
            self.cookie.copy() if self.cookie and isinstance(self.cookie, dict) else {}
        )

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
            self.check_result_code(result)
            return result["result"]
        except requests.exceptions.RequestException as e:
            print(
                f"Error fetching detailed bangumi info for season_id {season_id}: {e}"
            )
            raise
        except json.JSONDecodeError:
            print(f"Error decoding JSON response for season_id {season_id}")
            raise
        except KeyError:
            print(f"Unexpected response structure for season_id {season_id}")
            raise

    def get_detailed_bangumi_info_from_ep_id(self, ep_id, headers=None):
        """根据 ep_id 获取番剧详细信息。"""
        if headers is None:
            headers = {}
        params = {"ep_id": ep_id}
        try:
            response = requests.get(
                "https://api.bilibili.com/pgc/view/web/season",
                params=params,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()
            self.check_result_code(result)
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

    def get_numbers_in_str(self, string):
        """从字符串中提取数字。"""
        # Using regex is more robust and efficient
        match = re.search(r"\d+", string)
        return match.group() if match else ""

    def get_detailed_info_from_url(self, url, headers=None):
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
            media_id = self.get_numbers_in_str(path)
            if not media_id:
                raise ValueError("Could not extract media ID from the URL.")
            print(f"media_id = {media_id}")
            season_id = self.get_bangumi_info(media_id, headers)["season_id"]
            return self.get_detailed_bangumi_info_from_season_id(season_id, headers)
        else:
            # Assume it's an episode URL
            ep_id = self.get_numbers_in_str(path)
            if not ep_id:
                raise ValueError("Could not extract episode ID from the URL.")
            print(f"ep_id = {ep_id}")
            return self.get_detailed_bangumi_info_from_ep_id(ep_id, headers)

    def get_bangumi_download_info(self, aid, cid, qn=DEFAULT_QN, headers=None):
        """获取特定视频的下载信息。"""
        if headers is None:
            headers = {}

        # Ensure referer is present
        headers = headers.copy()
        # print(f"\nget_bangumi_download_info headers: {headers}")
        # print(f"\nget_bangumi_download_info cookie: {self.cookie}")
        headers.setdefault("referer", "https://www.bilibili.com")

        params = {"aid": aid, "cid": cid, "qn": qn, "fnval": DEFAULT_FNVAL}
        try:
            response = requests.get(
                "https://api.bilibili.com/pgc/player/web/playurl",
                headers=headers,
                params=params,
                cookies=self.cookie,
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()
            self.check_result_code(result)
            # print(f"\n\nresult: {result}\n\n")
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

    def sanitize_filename(self, filename):
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

    def get_bangumi_downloads(self, aid, cid, qn=DEFAULT_QN, headers=None):
        """获取视频和音频的下载链接列表。"""
        if headers is None:
            headers = {}
        try:
            ret = self.get_bangumi_download_info(aid, cid, qn, headers)
            downinfo = ret["dash"]
            support_formats = ret["support_formats"]
            # 查找对应项
            selected_format = None
            qn_quality_format = next(
                (f for f in support_formats if f["quality"] == qn), None
            )

            # 检查是否找到
            if qn_quality_format:
                print(f"找到对应格式: {qn_quality_format}")
                selected_format = qn_quality_format
            else:
                print(f"未找到对应格式: {qn}, 选择支持的最优清晰度格式")
                max_quality_format = max(support_formats, key=lambda x: x["quality"])
                selected_format = max_quality_format

            # print(f"最优清晰度格式 selected_format: {selected_format}")
            quality = selected_format["quality"]
            first_codecs = (
                selected_format["codecs"][0]
                if selected_format and selected_format["codecs"]
                else None
            )

            print(f"最优清晰度格式: {quality}")
            print(f"最优清晰度格式 first_codec: {first_codecs}")

            audios = downinfo["audio"]
            videos = downinfo["video"]

            video = next(
                (
                    f
                    for f in videos
                    if (f["id"] == quality and f["codecs"] == first_codecs)
                ),
                None,
            )
            audio = max(audios, key=lambda x: x["id"])

            # print(f"selected_format: {selected_format}")
            # print(f"video: {video}")
            # print(f"audio: {audio}")

            # Return lists of URLs
            return (selected_format, video, audio)
        except (KeyError, IndexError) as e:
            print(f"Error parsing download URLs for aid={aid}, cid={cid}: {e}")
            raise

    def download_bangumi(
        self,
        url,
        dest,
        headers=None,
        num=16,
        refurl="",
        downloader_type=DEFAULT_DOWNLOADER,
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

        print("\nheader: {}".format(headers))

        # Select downloader based on type
        if downloader_type.lower() == "aria2":
            downloader = DownloaderAria2(url, num, dest, header=headers)
        else:
            downloader = DownloaderAxel(url, num, dest, header=headers)

        if not downloader.run():
            print(f"\x1b[031mDownload failed: {url} -> {dest}\x1b[0m")
            return False  # Indicate failure
        return True  # Indicate success

    def download_all_from_info_with_quality(
        self,
        info,
        destdir,
        quality=DEFAULT_QN,
        doclean=False,
        headers=None,
        downloader_type=DEFAULT_DOWNLOADER,
    ):
        """根据番剧信息下载所有集数并合并。"""
        if headers is None:
            headers = {}

        if not info or "episodes" not in info:
            print("Invalid info structure provided for download.")
            return

        episodes = info["episodes"]
        if not episodes:
            print("No episodes found to download.")
            return

        print(f"Found {len(episodes)} episodes to download.")

        audio_files = []
        video_files = []
        merged_files = []

        # Create download directory
        os.makedirs(destdir, exist_ok=True)

        # Create or clear download list file
        download_list_path = os.path.join(destdir, "download_list.txt")
        with open(download_list_path, "w", encoding="utf-8") as f:
            f.write("# Bilibili Bangumi Downloader - Download List\n")
            f.write(f"# Total episodes: {len(episodes)}\n")
            f.write(f"# Download directory: {destdir}\n")
            f.write("# Format: Episode Title | Audio File | Video File | Merged File\n")
            f.write(f"# Selected quality: {quality}\n")
            f.write("# Status: Planned\n\n")

        enumerate_path = os.path.join(destdir, "enumerate.txt")
        with open(enumerate_path, "w", encoding="utf-8") as f:
            f.write("# Bilibili Bangumi Downloader - enumerate \n\n")

        for i, ep in enumerate(episodes):
            try:
                aid = ep["aid"]
                cid = ep["cid"]
                refurl = ep.get("share_url", "")  # Use .get for safety

                format, video, audio = self.get_bangumi_downloads(
                    aid, cid, quality, headers
                )

                if video is None:
                    print(f"视频信息不存在，跳过")
                    continue

                aurl = audio["base_url"]
                vurl = video["base_url"]

                enumerate_path = os.path.join(destdir, "enumerate.txt")
                with open(enumerate_path, "a", encoding="utf-8") as f:
                    f.write("# Bilibili Bangumi Downloader - enumerate \n\n")
                    f.write(f"# i: {i}\n")
                    f.write(f"# aid: {aid}\n")
                    f.write(f"# cid: {cid}\n")
                    f.write(f"# refurl: {refurl}\n\n")
                    f.write(f"# aurl: {aurl}\n")
                    f.write(f"# vurl: {vurl}\n\n\n")

                # 清晰度
                # description = selected_format["description"]
                new_description = format["new_description"]
                display_desc = format["display_desc"]
                quality = format["quality"]
                video_format = format["format"]

                # 使用从API返回的剧集标题作为文件名
                # share_copy show_title long_title
                episode_title = (
                    ep.get("share_copy", f"Episode_{i+1}")
                    + new_description
                    + display_desc
                )
                episode_title_safe = self.sanitize_filename(episode_title)

                print(
                    f"Downloading Episode {i+1}/{len(episodes)}: {episode_title_safe} (aid={aid}, cid={cid})"
                )

                print(f"\nbegin to download {episode_title_safe}")

                # Define file paths using episode title
                audio_dest = os.path.join(destdir, f"{episode_title_safe}.ogg")
                video_dest = os.path.join(
                    destdir, f"{episode_title_safe}.{video_format}"
                )
                merged_dest = os.path.join(destdir, f"{episode_title_safe}.mkv")

                # Record download info to file
                with open(download_list_path, "a", encoding="utf-8") as f:
                    f.write(
                        f"{episode_title_safe} | {os.path.basename(audio_dest)} | {os.path.basename(video_dest)} | {os.path.basename(merged_dest)}\n"
                    )

                # Download audio
                print("\n  Downloading audio...")
                if not self.download_bangumi(
                    aurl,
                    audio_dest,
                    headers=headers,
                    refurl=refurl,
                    downloader_type=downloader_type,
                ):
                    print(f"\n Failed to download audio for episode {i+1}. Skipping.")
                    # Update download list status
                    with open(download_list_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    with open(download_list_path, "w", encoding="utf-8") as f:
                        for line in lines[:-1]:  # All lines except the last one
                            f.write(line)
                        # Add status to the last line
                        last_line = lines[-1].strip()
                        f.write(f"{last_line} # Status: Audio Failed\n")
                    continue  # Skip to next episode if audio fails

                # Download video
                print(f"\n  Downloading video...")
                if not self.download_bangumi(
                    vurl,
                    video_dest,
                    headers=headers,
                    refurl=refurl,
                    downloader_type=downloader_type,
                ):
                    print(
                        f"\n  Failed to download video for episode {i+1}. Cleaning up audio and skipping."
                    )
                    # Update download list status
                    with open(download_list_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    with open(download_list_path, "w", encoding="utf-8") as f:
                        for line in lines[:-1]:  # All lines except the last one
                            f.write(line)
                        # Add status to the last line
                        last_line = lines[-1].strip()
                        f.write(f"{last_line} # Status: Video Failed\n")
                    # Clean up downloaded audio file if video fails
                    if os.path.exists(audio_dest):
                        os.remove(audio_dest)
                    continue  # Skip to next episode if video fails

                # If both downloads succeed, add to lists for merging
                audio_files.append(audio_dest)
                video_files.append(video_dest)

            except Exception as e:
                print(f"Error processing episode {i+1}: {e}")
                # Optionally, clean up partial downloads here if needed
                # But it's complex without knowing which files were created in this iteration
                # We rely on the final cleanup loop for now.
                continue  # Continue with next episode

        # Merge downloaded files
        if audio_files and video_files:
            print(f"\nMerging {len(audio_files)} episodes...")
            for i, (apath, vpath) in enumerate(zip(audio_files, video_files)):
                try:
                    # 从音频文件路径提取文件名（不含扩展名）作为合并后的文件名
                    base_name = os.path.splitext(os.path.basename(apath))[0]
                    opath = os.path.join(destdir, f"{base_name}.mkv")

                    print(f"  Merging episode {i+1}: {base_name}...")
                    if VAMerger(apath, vpath, opath).run():
                        print(f"  Merged episode {i+1} successfully.")
                        merged_files.append(opath)
                        if doclean:
                            os.remove(apath)
                            os.remove(vpath)

                        # Update download list status
                        download_list_path = os.path.join(destdir, "download_list.txt")
                        with open(download_list_path, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                        with open(download_list_path, "w", encoding="utf-8") as f:
                            for line in lines:
                                if (
                                    f"{base_name}.ogg" in line
                                    and f"{base_name}.flv" in line
                                ):
                                    if doclean:
                                        f.write(
                                            f"{line.strip()} # Status: Merged (files cleaned)\n"
                                        )
                                    else:
                                        f.write(f"{line.strip()} # Status: Merged\n")
                                else:
                                    f.write(line)
                    else:
                        print(f"  Failed to merge episode {i+1}.")

                        # Update download list status
                        download_list_path = os.path.join(destdir, "download_list.txt")
                        with open(download_list_path, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                        with open(download_list_path, "w", encoding="utf-8") as f:
                            for line in lines:
                                if (
                                    f"{base_name}.ogg" in line
                                    and f"{base_name}.flv" in line
                                ):
                                    f.write(f"{line.strip()} # Status: Merge Failed\n")
                                else:
                                    f.write(line)
                except Exception as e:
                    print(f"Error merging episode {i+1}: {e}")
        else:
            print("No episodes were successfully downloaded to merge.")

        return merged_files

    def download_all_from_info(
        self,
        info,
        destdir,
        doclean=False,
        headers=None,
        downloader_type=DEFAULT_DOWNLOADER,
    ):
        """根据番剧信息下载所有集数并合并。为了向后兼容，使用默认清晰度。"""
        return self.download_all_from_info_with_quality(
            info, destdir, DEFAULT_QN, doclean, headers, downloader_type
        )
