#!/usr/bin/env python3

import os
import sys

from bangumi_downloader import BangumiDownloader

# 默认的 HTTP 请求头
# DEFAULT_HEADERS = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Connection': 'keep-alive',
#     'Upgrade-Insecure-Requests': '1',
# }
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}
# 可用的下载器选项
AVAILABLE_DOWNLOADERS = ["axel", "aria2"]


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


def get_cookie():
    """尝试从文件读取 Cookie，如果失败则提示用户输入。"""
    cookie = ""
    # 尝试使用 __file__ 获取更可靠的脚本路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_file_path = os.path.join(script_dir, "cookie.txt")

    if os.path.exists(cookie_file_path):
        try:
            with open(cookie_file_path, "r") as f:
                cookie = f.read().strip()
        except Exception as e:
            print(f"Warning: Could not read cookie from {cookie_file_path}: {e}")
            print("Please paste your cookie when prompted.")
    else:
        print(f"Info: Cookie file not found at {cookie_file_path}.")
        print("Please paste your cookie when prompted.")

    if not cookie:
        cookie = input("Please paste your Bilibili cookie: ").strip()
        if not cookie:
            print("Error: Cookie is required.")
            sys.exit(1)

    return convert_cookie_to_dict(cookie)


def get_user_input():
    """获取用户输入的 URL、下载目录、清晰度选项、清理选项和下载器类型。"""
    # 从用户获取输入，如果直接回车则使用默认值
    video_url = input(
        "Enter Video URL (default: https://www.bilibili.com/bangumi/play/ep836727?spm_id_from=333.1387.0.0&from_spmid=666.25.episode.0): "
    ).strip()
    if not video_url:
        video_url = "https://www.bilibili.com/bangumi/play/ep836727?spm_id_from=333.1387.0.0&from_spmid=666.25.episode.0"

    record_url = input(
        "Enter Download Directory (default: /Users/wtf/Movies/bili_downloader/牧神记): "
    ).strip()
    if not record_url:
        record_url = "G:/LLM/ghost_download/bilibili/video/牧神记"

    doclean_input = (
        input("Clean .flv/.ogg files after merging? [y/N] (default N): ")
        .strip()
        .lower()
    )
    doclean = doclean_input in ("y", "yes")

    # 显示清晰度选项并获取用户选择
    from bangumi_downloader import DEFAULT_QN, QUALITY_OPTIONS

    print("\nAvailable quality options:")
    for qn, desc in QUALITY_OPTIONS.items():
        default_mark = " (default)" if qn == DEFAULT_QN else ""
        print(f"  {qn}: {desc}{default_mark}")

    while True:
        quality_choice = input(
            f"\nSelect quality (enter number, default {DEFAULT_QN}): "
        ).strip()
        if not quality_choice:
            selected_qn = DEFAULT_QN
            break
        try:
            selected_qn = int(quality_choice)
            if selected_qn in QUALITY_OPTIONS:
                break
            else:
                print(f"Please enter a valid quality number from the options above.")
        except ValueError:
            print("Please enter a valid number.")

    print("Available downloaders:")
    for i, dl in enumerate(AVAILABLE_DOWNLOADERS, 1):
        print(f"  {i}. {dl}")

    while True:
        downloader_choice = input(
            f"Select downloader (1-{len(AVAILABLE_DOWNLOADERS)}, default 1 for axel): "
        ).strip()
        if not downloader_choice:
            downloader_type = AVAILABLE_DOWNLOADERS[0]  # 默认为第一个选项 axel
            break
        try:
            choice_index = int(downloader_choice) - 1
            if 0 <= choice_index < len(AVAILABLE_DOWNLOADERS):
                downloader_type = AVAILABLE_DOWNLOADERS[choice_index]
                break
            else:
                print(
                    f"Please enter a number between 1 and {len(AVAILABLE_DOWNLOADERS)}."
                )
        except ValueError:
            print("Please enter a valid number.")

    record_url = os.path.abspath(os.path.expanduser(record_url))

    # 简单验证目录路径（不检查父目录权限）
    if os.path.exists(record_url) and not os.path.isdir(record_url):
        print(f"Error: {record_url} exists but is not a directory.")
        sys.exit(1)

    return video_url, record_url, selected_qn, doclean, downloader_type


if __name__ == "__main__":
    try:
        # Cookie
        cookie = get_cookie()

        # Input
        video_url, record_url, selected_qn, doclean, downloader_type = get_user_input()

        print(
            f"Downloading from {video_url} to {record_url} with quality {selected_qn} using {downloader_type}"
        )

        # Create downloader instance
        downloader = BangumiDownloader(cookie)
        print("\nbegin to get detail info")
        # Download with default headers
        info = downloader.get_detailed_info_from_url(video_url, DEFAULT_HEADERS)
        # print(f"\nget detail info: {info}")
        # Pass the selected quality to the download function
        merged_files = downloader.download_all_from_info_with_quality(
            info, record_url, selected_qn, doclean, DEFAULT_HEADERS, downloader_type
        )
        print(f"\nDownload completed. Merged {len(merged_files)} files:")
        for file in merged_files:
            print(f"  - {file}")

    except KeyboardInterrupt:
        print("\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
