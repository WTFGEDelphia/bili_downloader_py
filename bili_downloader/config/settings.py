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

    def save_to_file(self) -> None:
        """保存配置到文件"""
        import toml

        config_file = self.get_config_file()
        with open(config_file, "w", encoding="utf-8") as f:
            toml.dump(self.model_dump(), f)
