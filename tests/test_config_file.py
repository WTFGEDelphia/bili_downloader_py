import pytest
import os
import tempfile
from pathlib import Path

from bili_downloader.config.settings import Settings


def test_settings_load_and_save():
    """测试配置文件的加载和保存功能"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 临时修改配置目录
        original_get_config_dir = Settings.get_config_dir
        Settings.get_config_dir = lambda: Path(temp_dir) / "config"
        
        try:
            # 测试配置文件不存在时创建默认配置
            settings = Settings.load_from_file()
            assert settings.download.default_quality == 112
            assert settings.download.default_downloader == "axel"
            
            # 验证配置文件已创建
            config_file = Settings.get_config_file()
            assert config_file.exists()
            
            # 修改配置并保存
            settings.download.default_quality = 80
            settings.save_to_file()
            
            # 重新加载配置验证修改已保存
            new_settings = Settings.load_from_file()
            assert new_settings.download.default_quality == 80
            
        finally:
            # 恢复原始方法
            Settings.get_config_dir = original_get_config_dir


def test_settings_priority():
    """测试配置优先级"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 临时修改配置目录
        original_get_config_dir = Settings.get_config_dir
        Settings.get_config_dir = lambda: Path(temp_dir) / "config"
        
        try:
            # 创建配置文件
            config_file = Settings.get_config_file()
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w", encoding="utf-8") as f:
                f.write("""[download]
default_quality = 64
default_downloader = "aria2"
""")
            
            # 测试文件配置
            settings = Settings.load_from_file()
            assert settings.download.default_quality == 64
            assert settings.download.default_downloader == "aria2"
            
            # 测试环境变量优先级（需要在创建Settings之前设置）
            os.environ["DOWNLOAD__DEFAULT_QUALITY"] = "32"
            settings_with_env = Settings()
            assert settings_with_env.download.default_quality == 32
            
            # 清理环境变量
            del os.environ["DOWNLOAD__DEFAULT_QUALITY"]
            
        finally:
            # 恢复原始方法
            Settings.get_config_dir = original_get_config_dir


if __name__ == "__main__":
    test_settings_load_and_save()
    test_settings_priority()
    print("All config tests passed!")