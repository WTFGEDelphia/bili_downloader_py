import os
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DownloadSettings(BaseModel):
    default_quality: int = Field(default=112, description="默认下载清晰度")
    default_downloader: str = Field(
        default="axel", description="默认下载器 (axel 或 aria2)"
    )
    default_threads: int = Field(default=16, description="默认下载线程数")
    cleanup_after_merge: bool = Field(
        default=False, description="合并后是否清理原始音视频文件"
    )


class HistorySettings(BaseModel):
    last_url: str = Field(default="", description="上次下载的URL")
    last_directory: str = Field(default="", description="上次下载的目录")


class NetworkSettings(BaseModel):
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        description="User-Agent 字符串",
    )

    @property
    def headers(self) -> dict:
        """获取默认请求头"""
        return {
            "User-Agent": self.user_agent,
            "Referer": "https://www.bilibili.com",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
        }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    download: DownloadSettings = DownloadSettings()
    history: HistorySettings = HistorySettings()
    network: NetworkSettings = NetworkSettings()

    @classmethod
    def get_config_dir(cls) -> Path:
        """获取配置文件目录"""
        # Windows: C:\Users\{username}\AppData\Roaming\bili-downloader
        # macOS: ~/Library/Application Support/bili-downloader
        # Linux: ~/.config/bili-downloader
        config_dir = Path.home() / ".config" / "bili-downloader"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @classmethod
    def get_config_file(cls) -> Path:
        """获取配置文件路径"""
        return cls.get_config_dir() / "config.toml"

    @classmethod
    def load_from_file(cls) -> "Settings":
        """从配置文件加载设置"""
        config_file = cls.get_config_file()
        if config_file.exists():
            # 如果配置文件存在，从文件加载
            # 使用配置文件作为 overrides，而不是完全替换默认值
            import toml

            with open(config_file, "r", encoding="utf-8") as f:
                config_data = toml.load(f)

            # 创建实例并应用配置文件中的设置
            settings = cls()
            if "download" in config_data:
                settings.download = DownloadSettings(**config_data["download"])
            if "history" in config_data:
                settings.history = HistorySettings(**config_data["history"])
            if "network" in config_data:
                settings.network = NetworkSettings(**config_data["network"])
            return settings
        else:
            # 如果配置文件不存在，使用默认设置并保存
            settings = cls()
            settings.save_to_file()
            return settings

    def save_to_file(self) -> None:
        """保存配置到文件"""
        try:
            import toml

            config_file = self.get_config_file()
            # 确保配置目录存在
            config_file.parent.mkdir(parents=True, exist_ok=True)

            # 转换为字典并保存
            config_dict = {
                "download": self.download.model_dump(),
                "history": self.history.model_dump(),
                "network": self.network.model_dump(),
            }

            with open(config_file, "w", encoding="utf-8") as f:
                toml.dump(config_dict, f)
        except Exception as e:
            # 如果保存失败，不抛出异常，但记录日志
            print(f"Warning: Could not save config to file: {e}")
