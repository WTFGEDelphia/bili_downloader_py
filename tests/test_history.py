#!/usr/bin/env python3

import os

# 添加项目根目录到Python路径
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bili_downloader.config.settings import Settings


def test_history_settings():
    """测试历史记录功能"""
    print("Testing history settings...")

    # 创建临时目录进行测试
    with tempfile.TemporaryDirectory() as temp_dir:
        # 保存原始方法
        original_get_config_dir = Settings.get_config_dir

        # 临时修改配置目录
        Settings.get_config_dir = classmethod(lambda cls: Path(temp_dir) / "config")

        try:
            print("1. Testing Settings.load_from_file()...")
            settings = Settings.load_from_file()
            print("   Settings loaded successfully!")
            print(f"   Default quality: {settings.download.default_quality}")
            print(f"   Default downloader: {settings.download.default_downloader}")
            print(f"   Last URL: '{settings.history.last_url}'")
            print(f"   Last directory: '{settings.history.last_directory}'")

            # 测试保存功能
            print("\n2. Testing Settings.save_to_file()...")
            settings.history.last_url = "https://www.bilibili.com/bangumi/play/ep123"
            settings.history.last_directory = "/test/downloads"
            settings.save_to_file()
            config_file = Settings.get_config_file()
            print(f"   Config file created at: {config_file}")
            if config_file.exists():
                print("   Config file exists!")
                with open(config_file, encoding="utf-8") as f:
                    content = f.read()
                    print("   Config file content:")
                    print(content)
            else:
                print("   Config file does not exist!")

            # 重新加载配置验证修改已保存
            print("\n3. Testing reloading settings...")
            new_settings = Settings.load_from_file()
            print(f"   Last URL: '{new_settings.history.last_url}'")
            print(f"   Last directory: '{new_settings.history.last_directory}'")

            # 验证历史记录已正确保存
            assert (
                new_settings.history.last_url
                == "https://www.bilibili.com/bangumi/play/ep123"
            )
            assert new_settings.history.last_directory == "/test/downloads"
            print("   History settings saved and loaded correctly!")

        finally:
            # 恢复原始方法
            Settings.get_config_dir = original_get_config_dir

    print("\nAll history tests passed!")


if __name__ == "__main__":
    test_history_settings()
