import json
import os
import re
from urllib.parse import urlparse

import requests

from bili_downloader.config.settings import Settings
from bili_downloader.core.downloader_aria2 import DownloaderAria2
from bili_downloader.core.downloader_axel import DownloaderAxel
from bili_downloader.core.vamerger import VAMerger
from bili_downloader.exceptions import APIError, DownloadError, MergeError
from bili_downloader.utils.logger import logger
from bili_downloader.utils.print_utils import print_warning

# 默认质量和格式参数
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

# 默认下载器类型
DEFAULT_DOWNLOADER = "aria2"  # 或 "axel"


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
            # 通过 "; " 或 ";" 分割以处理不同格式
            # 然后通过第一个 "=" 分割以分离键和值
            cookies = {}
            # 首先尝试通过 "; " 分割
            cookie_parts = cookie.split("; ")
            # 如果不行，尝试通过 ";" 分割
            if len(cookie_parts) <= 1:
                cookie_parts = cookie.split(";")

            for part in cookie_parts:
                part = part.strip()  # 移除前导/尾随空格
                if not part:
                    continue
                # 通过第一个 "=" 分割以处理可能包含 "=" 的值
                if "=" in part:
                    key, value = part.split("=", 1)
                    # 对于某些可能有特殊字符的cookie键，
                    # 我们需要确保它们正确格式化以用于HTTP头
                    # cookie值中的某些字符可能会导致HTTP头问题
                    cookies[key] = value
            return cookies
        except Exception as e:
            # 处理cookie字符串格式错误的情况
            print_warning(f"Cookie字符串可能格式错误: {e}")
            return {}

    def check_result_code(self, result):
        """检查 API 返回的业务逻辑错误码。"""
        if result.get("code") != 0:
            logger.error("API错误", result=result)
            # 使用异常而不是sys.exit以获得更好的错误处理
            raise APIError(f"API返回错误码 {result.get('code')}")

    def get_bangumi_info(self, media_id, headers=None):
        """根据 media_id 获取番剧基础信息。"""
        # 加载全局设置以获取User-Agent
        settings = Settings.load_from_file()
        
        if headers is None:
            headers = {}

        # 确保必要的请求头存在
        headers = headers.copy()
        headers.setdefault(
            "User-Agent",
            settings.network.user_agent,
        )
        headers.setdefault("Referer", "https://www.bilibili.com")

        # 复制cookie字典以避免修改原始数据
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
            response.raise_for_status()  # 对于错误响应(4xx或5xx)抛出HTTPError
            result = response.json()
            self.check_result_code(result)
            return result["result"]["media"]
        except requests.exceptions.RequestException as e:
            logger.error(f"获取番剧信息时HTTP错误，媒体ID: {media_id}", error=str(e))
            raise DownloadError(f"获取番剧信息时出错 media_id {media_id}: {e}") from e
        except json.JSONDecodeError:
            logger.error(
                f"解析媒体ID的JSON响应时出错，媒体ID: {media_id}", error=str(e)
            )
            raise DownloadError(f"解析JSON响应时出错 media_id {media_id}")
        except KeyError:
            logger.error("媒体ID的响应结构异常", media_id=media_id)
            raise DownloadError(f"媒体ID的响应结构异常 {media_id}")

    def get_bangumi_info_by_season_id(self, season_id, headers=None):
        """根据 season_id 获取番剧信息。"""
        # 加载全局设置以获取User-Agent
        settings = Settings.load_from_file()
        
        if headers is None:
            headers = {}

        # 确保必要的请求头存在
        headers = headers.copy()
        headers.setdefault(
            "User-Agent",
            settings.network.user_agent,
        )
        headers.setdefault("Referer", "https://www.bilibili.com")

        # 复制cookie字典以避免修改原始数据
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
            )
            response.raise_for_status()
            result = response.json()
            self.check_result_code(result)
            return result["result"]
        except requests.exceptions.RequestException as e:
            logger.error(
                "获取番剧详细信息时出错，season_id",
                season_id=season_id,
                error=str(e),
            )
            raise DownloadError(
                f"获取番剧详细信息时出错 season_id {season_id}: {e}"
            ) from e
        except json.JSONDecodeError:
            logger.error("解析season_id的JSON响应时出错", season_id=season_id)
            raise DownloadError(f"解析JSON响应时出错 season_id {season_id}")
        except KeyError:
            logger.error("season_id的响应结构异常", season_id=season_id)
            raise DownloadError(f"season_id的响应结构异常 {season_id}")

    def get_bangumi_info_by_ep_id(self, ep_id, headers=None):
        """根据 ep_id 获取番剧详细信息。"""
        # 加载全局设置以获取User-Agent
        settings = Settings.load_from_file()
        
        if headers is None:
            headers = {}

        # 确保必要的请求头存在
        headers = headers.copy()
        headers.setdefault(
            "User-Agent",
            settings.network.user_agent,
        )
        headers.setdefault("Referer", "https://www.bilibili.com")

        logger.info(f"Headers are {headers}")
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
            logger.error(
                "获取番剧详细信息时出错，ep_id",
                ep_id=ep_id,
                error=str(e),
            )
            raise DownloadError(f"获取番剧详细信息时出错 ep_id {ep_id}: {e}") from e
        except json.JSONDecodeError:
            logger.error(f"解析剧集ID的JSON响应时出错，剧集ID: {ep_id}", error=str(e))
            raise DownloadError(f"解析剧集ID的JSON响应时出错，剧集ID: {ep_id}") from e

    def get_numbers_in_str(self, string: str) -> str:
        """从字符串中提取数字。"""
        # 使用正则表达式更健壮和高效
        match = re.search(r"\d+", string)
        return match.group() if match else ""
        """根据 URL 解析并获取番剧详细信息。"""
        if headers is None:
            headers = {}

        url = url.rstrip("/")
        parsed_url = urlparse(url)

        if not parsed_url.netloc or not parsed_url.scheme:
            raise ValueError("提供了无效的URL。")

        path = parsed_url.path

        if "/bangumi/media/" in path:
            # 从类似 /bangumi/media/md191 的路径中提取 media ID
            media_id = self.get_numbers_in_str(path)
            if not media_id:
                raise ValueError("Could not extract media ID from the URL.")
            logger.info("Extracted media_id", media_id=media_id)
            season_id = self.get_bangumi_info(media_id, headers)["season_id"]
            return self.get_detailed_bangumi_info_from_season_id(season_id, headers)
        else:
            # 假设是剧集URL
            ep_id = self.get_numbers_in_str(path)
            if not ep_id:
                raise ValueError("Could not extract episode ID from the URL.")
            logger.info("Extracted ep_id", ep_id=ep_id)
            return self.get_detailed_bangumi_info_from_ep_id(ep_id, headers)

    def get_bangumi_download_info(self, aid, cid, qn=DEFAULT_QN, headers=None):
        """获取特定视频的下载信息。"""
        if headers is None:
            headers = {}

        # 确保referer存在
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
            logger.error(
                f"获取剧集下载信息时出错，aid: {aid}, cid: {cid}", error=str(e)
            )
            raise DownloadError(f"获取下载信息时出错 aid={aid}, cid={cid}: {e}") from e
        except json.JSONDecodeError:
            logger.error(f"解析JSON响应时出错，aid: {aid}, cid: {cid}")
            raise DownloadError(f"解析JSON响应时出错 aid={aid}, cid={cid}")
        except KeyError:
            logger.error("响应结构异常", aid=aid, cid=cid)
            raise DownloadError(f"响应结构异常 aid={aid}, cid={cid}")

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
                logger.info("Found matching format", format=qn_quality_format)
                selected_format = qn_quality_format
            else:
                logger.warning(
                    "No matching format found, selecting the best available quality format",
                    qn=qn,
                )
                max_quality_format = max(support_formats, key=lambda x: x["quality"])
                selected_format = max_quality_format

            quality = selected_format["quality"]
            first_codecs = (
                selected_format["codecs"][0]
                if selected_format and selected_format["codecs"]
                else None
            )

            logger.info(
                "Best quality format", quality=quality, first_codec=first_codecs
            )

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

            # 返回URL列表
            return (selected_format, video, audio)
        except (KeyError, IndexError) as e:
            logger.error("解析下载URL时出错", aid=aid, cid=cid, error=str(e))
            raise DownloadError(f"解析下载URL时出错 aid={aid}, cid={cid}: {e}") from e

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

        # 确保referer存在并正确格式化
        headers = headers.copy()
        referer_value = refurl or "https://www.bilibili.com"
        # 确保referer值是字符串且不包含问题字符
        if isinstance(referer_value, str):
            # 移除可能导致问题的控制字符
            referer_value = "".join(char for char in referer_value if ord(char) >= 32)
        headers.setdefault("referer", referer_value)

        # 如果目录不存在则创建
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        logger.info("正在下载文件", url=url, dest=dest, referer=referer_value)

        # 根据类型选择下载器
        if downloader_type.lower() == "aria2":
            downloader = DownloaderAria2(url, num, dest, header=headers)
        else:
            downloader = DownloaderAxel(url, num, dest, header=headers)

        if not downloader.run():
            logger.error("下载失败", url=url, dest=dest)
            raise DownloadError(f"下载失败: {url} -> {dest}")
        return True  # 表示成功

    def download_all_from_info_with_quality(
        self,
        info,
        destdir,
        quality=DEFAULT_QN,
        doclean=False,
        headers=None,
        downloader_type=DEFAULT_DOWNLOADER,
        keyword="",
        threads=16,
    ):
        """根据番剧信息下载所有集数并合并。"""
        if headers is None:
            headers = {}

        if not info or "episodes" not in info:
            logger.error("提供的信息结构无效")
            return

        episodes = info["episodes"]
        if not episodes:
            logger.warning("未找到可下载的剧集")
            return

        logger.info("发现可下载的剧集", count=len(episodes))

        merged_files = []

        # 创建下载目录
        os.makedirs(destdir, exist_ok=True)

        # 创建或清空下载列表文件
        download_list_path = os.path.join(destdir, "download_list.txt")
        with open(download_list_path, "w", encoding="utf-8") as f:
            f.write("# Bilibili Bangumi Downloader - 下载列表\n")
            f.write(f"# 总剧集数: {len(episodes)}\n")
            f.write(f"# 下载目录: {destdir}\n")
            f.write("# 格式: 剧集标题 | 音频文件 | 视频文件 | 合并文件\n")
            f.write(f"# 选择的清晰度: {quality}\n")
            f.write("# 状态: 计划中\n\n")

        enumerate_path = os.path.join(destdir, "enumerate.txt")
        with open(enumerate_path, "w", encoding="utf-8") as f:
            f.write("# Bilibili Bangumi Downloader - 枚举信息 \n\n")

        for i, ep in enumerate(episodes):
            try:
                aid = ep["aid"]
                cid = ep["cid"]
                refurl = ep.get("share_url", "")  # 使用 .get 保证安全

                format, video, audio = self.get_bangumi_downloads(
                    aid, cid, quality, headers
                )

                if video is None:
                    logger.warning("Video information does not exist, skipping")
                    continue

                aurl = audio["base_url"]
                vurl = video["base_url"]

                # 记录调试信息到文件
                enumerate_path = os.path.join(destdir, "enumerate.txt")
                with open(enumerate_path, "a", encoding="utf-8") as f:
                    f.write("# Bilibili Bangumi Downloader - 枚举信息 \n\n")
                    f.write(f"# 序号: {i}\n")
                    f.write(f"# aid: {aid}\n")
                    f.write(f"# cid: {cid}\n")
                    f.write(f"# refurl: {refurl}\n\n")
                    f.write(f"# 音频URL: {aurl}\n")
                    f.write(f"# 视频URL: {vurl}\n\n\n")

                # 清晰度
                new_description = format["new_description"]
                display_desc = format["display_desc"]
                quality = format["quality"]
                video_format = format["format"]

                # 使用从API返回的剧集标题作为文件名
                episode_title = (
                    ep.get("share_copy", f"Episode_{i+1}")
                    + new_description
                    + display_desc
                )
                episode_title_safe = self.sanitize_filename(episode_title)

                # 检查关键字过滤
                if keyword and keyword not in episode_title_safe:
                    logger.info(
                        f"跳过剧集 {i+1}/{len(episodes)}: {episode_title_safe} (关键字过滤: {keyword})"
                    )
                    continue

                logger.info(
                    f"正在下载剧集 {i+1}/{len(episodes)}: {episode_title_safe} (aid={aid}, cid={cid})"
                )

                logger.info(f"开始下载 {episode_title_safe}")

                # 使用剧集标题定义文件路径
                audio_dest = os.path.join(destdir, f"{episode_title_safe}.ogg")
                video_dest = os.path.join(
                    destdir, f"{episode_title_safe}.{video_format}"
                )
                merged_dest = os.path.join(destdir, f"{episode_title_safe}.mkv")

                # 检查目标文件是否已存在，如果存在则跳过下载和合并
                if os.path.exists(merged_dest):
                    logger.info(f"目标文件已存在，跳过下载和合并: {merged_dest}")
                    merged_files.append(merged_dest)

                    # 更新下载列表状态
                    with open(download_list_path, "a", encoding="utf-8") as f:
                        f.write(
                            f"{episode_title_safe} | {os.path.basename(audio_dest)} | {os.path.basename(video_dest)} | {os.path.basename(merged_dest)} # 状态: 已跳过 (文件已存在)\n"
                        )
                    continue

                # 检查是否存在未完成的下载文件 (.st 或 .aria2)，如果存在则需要重新下载
                def has_incomplete_download(file_path):
                    return os.path.exists(file_path + ".st") or os.path.exists(
                        file_path + ".aria2"
                    )

                audio_incomplete = has_incomplete_download(audio_dest)
                video_incomplete = has_incomplete_download(video_dest)

                # 如果文件存在但下载未完成，删除原文件和未完成的文件
                if os.path.exists(audio_dest) and audio_incomplete:
                    logger.info(f"音频文件下载未完成，删除并重新下载: {audio_dest}")
                    os.remove(audio_dest)
                    if os.path.exists(audio_dest + ".st"):
                        os.remove(audio_dest + ".st")
                    if os.path.exists(audio_dest + ".aria2"):
                        os.remove(audio_dest + ".aria2")
                    audio_exists = False
                elif os.path.exists(audio_dest):
                    audio_exists = True
                else:
                    audio_exists = False

                if os.path.exists(video_dest) and video_incomplete:
                    logger.info(f"视频文件下载未完成，删除并重新下载: {video_dest}")
                    os.remove(video_dest)
                    if os.path.exists(video_dest + ".st"):
                        os.remove(video_dest + ".st")
                    if os.path.exists(video_dest + ".aria2"):
                        os.remove(video_dest + ".aria2")
                    video_exists = False
                elif os.path.exists(video_dest):
                    video_exists = True
                else:
                    video_exists = False

                # 检查音频和视频文件是否都已存在
                if audio_exists and video_exists:
                    logger.info(
                        f"音频和视频文件已存在，跳过下载，直接合并: {episode_title_safe}"
                    )
                else:
                    # 记录下载信息到文件
                    with open(download_list_path, "a", encoding="utf-8") as f:
                        f.write(
                            f"{episode_title_safe} | {os.path.basename(audio_dest)} | {os.path.basename(video_dest)} | {os.path.basename(merged_dest)}\n"
                        )

                    # 下载音频 (如果不存在)
                    if not audio_exists:
                        logger.info("正在下载音频...")
                        try:
                            self.download_bangumi(
                                aurl,
                                audio_dest,
                                headers=headers,
                                refurl=refurl,
                                downloader_type=downloader_type,
                                num=threads,
                            )
                        except DownloadError as e:
                            logger.error(
                                f"下载第 {i+1} 集音频失败。跳过。",
                                error=str(e),
                            )
                            # 更新下载列表状态
                            with open(download_list_path, encoding="utf-8") as f:
                                lines = f.readlines()
                            with open(download_list_path, "w", encoding="utf-8") as f:
                                for line in lines[:-1]:  # 除最后一行外的所有行
                                    f.write(line)
                                # 为最后一行添加状态
                                last_line = lines[-1].strip()
                                f.write(f"{last_line} # 状态: 音频下载失败\n")
                            continue  # 如果音频下载失败则跳过此剧集
                    else:
                        logger.info(f"音频文件已存在，跳过下载: {audio_dest}")

                    # 下载视频 (如果不存在)
                    if not video_exists:
                        logger.info("正在下载视频...")
                        try:
                            self.download_bangumi(
                                vurl,
                                video_dest,
                                headers=headers,
                                refurl=refurl,
                                downloader_type=downloader_type,
                                num=threads,
                            )
                        except DownloadError as e:
                            logger.error(
                                f"下载第 {i+1} 集视频失败。清理音频并跳过。",
                                error=str(e),
                            )
                            # 更新下载列表状态
                            with open(download_list_path, encoding="utf-8") as f:
                                lines = f.readlines()
                            with open(download_list_path, "w", encoding="utf-8") as f:
                                for line in lines[:-1]:  # 除最后一行外的所有行
                                    f.write(line)
                                # 为最后一行添加状态
                                last_line = lines[-1].strip()
                                f.write(f"{last_line} # 状态: 视频下载失败\n")
                            # 如果视频下载失败且刚下载了音频，则清理已下载的音频文件
                            if not audio_exists and os.path.exists(audio_dest):
                                os.remove(audio_dest)
                            continue  # 如果视频下载失败则跳过此剧集
                    else:
                        logger.info(f"视频文件已存在，跳过下载: {video_dest}")

                # 立即合并下载的音频和视频文件（优先下载合并）
                logger.info(f"正在合并第 {i+1} 集: {episode_title_safe}...")
                if VAMerger(audio_dest, video_dest, merged_dest).run():
                    logger.info(f"第 {i+1} 集合并成功。")
                    merged_files.append(merged_dest)
                    if doclean:
                        os.remove(audio_dest)
                        os.remove(video_dest)

                    # 更新下载列表状态
                    with open(download_list_path, encoding="utf-8") as f:
                        lines = f.readlines()
                    with open(download_list_path, "w", encoding="utf-8") as f:
                        for line in lines:
                            if (
                                f"{os.path.basename(audio_dest)}" in line
                                and f"{os.path.basename(video_dest)}" in line
                            ):
                                if doclean:
                                    f.write(
                                        f"{line.strip()} # 状态: 已合并 (文件已清理)\n"
                                    )
                                else:
                                    f.write(f"{line.strip()} # 状态: 已合并\n")
                            else:
                                f.write(line)
                else:
                    logger.error(f"第 {i+1} 集合并失败。")
                    # 更新下载列表状态
                    with open(download_list_path, encoding="utf-8") as f:
                        lines = f.readlines()
                    with open(download_list_path, "w", encoding="utf-8") as f:
                        for line in lines:
                            if (
                                f"{os.path.basename(audio_dest)}" in line
                                and f"{os.path.basename(video_dest)}" in line
                            ):
                                f.write(f"{line.strip()} # 状态: 合并失败\n")
                            else:
                                f.write(line)
                    raise MergeError(f"第 {i+1} 集合并失败。")

            except Exception as e:
                logger.error(f"处理第 {i+1} 集时出错", error=str(e))
                continue  # 继续处理下一集

        logger.info(f"下载和合并完成。共合并 {len(merged_files)} 个文件:")
        for file in merged_files:
            logger.info(f"  - {file}")

        return merged_files
