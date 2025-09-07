import os
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from bili_downloader.utils.print_utils import print_info, print_warning


class LogSettings(BaseModel):
    """日志设置"""

    enable_file_logging: bool = Field(default=False, description="是否启用文件日志记录")
    log_file_path: str = Field(
        default="logs/bili_downloader.log", description="日志文件路径"
    )
    log_level: str = Field(
        default="INFO", description="日志级别 (DEBUG, INFO, WARNING, ERROR)"
    )
    max_log_file_size: int = Field(
        default=10 * 1024 * 1024, description="最大日志文件大小(字节)，默认10MB"
    )
    backup_count: int = Field(default=5, description="保留的备份日志文件数量")
    log_format: str = Field(
        default="simple", description="日志格式 (json, console, keyvalue, simple)"
    )


class DownloadSettings(BaseModel):
    default_quality: int = Field(default=112, description="默认下载清晰度")
    default_downloader: str = Field(
        default="axel", description="默认下载器 (axel 或 aria2)"
    )
    default_threads: int = Field(default=16, description="默认下载线程数")
    cleanup_after_merge: bool = Field(
        default=False, description="合并后是否清理原始音视频文件"
    )


class LoginSettings(BaseModel):
    default_method: str = Field(default="qr", description="默认登录方法 (qr 或 web)")
    default_output: str = Field(default="", description="默认Cookie输出文件, 用户缓存目录")
    default_timeout: int = Field(default=180, description="QR码登录超时时间(秒)")


class HistorySettings(BaseModel):
    last_url: str = Field(default="", description="上次下载的URL")
    last_directory: str = Field(default="", description="上次下载的目录")


class NetworkSettings(BaseModel):
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
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

    log: LogSettings = LogSettings()
    download: DownloadSettings = DownloadSettings()
    login: LoginSettings = LoginSettings()
    history: HistorySettings = HistorySettings()
    network: NetworkSettings = NetworkSettings()

    def model_post_init(self, __context) -> None:
        self.login.default_output = str(self.get_env_cookie_file_path())

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
    def get_cookie_file(cls) -> Path:
        """获取配置文件路径"""
        cookie_path = cls.get_config_dir() / "cookie.txt"
        return cookie_path

    @classmethod
    def get_env_config_file_path(cls) -> Path:
        """
        获取环境变量中指定的配置文件路径

        Returns:
            Path: 配置文件路径
        """
        # 获取 CACHE__CONFIG_PATH 环境变量指定的配置文件路径
        config_file_path = os.environ.get("CACHE__CONFIG_PATH")
        if config_file_path:
            return Path(config_file_path)
        else:
            # 如果未指定，则使用默认配置文件路径
            return cls.get_config_file()

    @classmethod
    def get_env_cookie_file_path(cls) -> Path:
        """
        获取环境变量中指定的Cookie文件路径

        Returns:
            Path: 配置文件路径
        """
        # 获取 LOGIN__DEFAULT_OUTPUT 环境变量指定的配置文件路径
        cookie_file_path = os.environ.get("LOGIN__DEFAULT_OUTPUT")
        if cookie_file_path:
            return Path(cookie_file_path)
        else:
            # 如果未指定，则使用默认配置文件路径
            return cls.get_cookie_file()

    @classmethod
    def load_from_file(cls) -> "Settings":
        """
        按照指定顺序加载配置:
        1. .env 文件 (如果不存在则复制 .env.example)
        2. 环境变量中CACHE__CONFIG_PATH的配置文件
        3. CACHE__CONFIG_PATH的值为空则保持当前逻辑
        4. .env中所有值为空的 配置文件也为空的 按照用户输入的为准
        5. 最后所有数据更新到配置文件，下次执行程序 读取仍然按照这个顺序

        Returns:
            Settings: 配置对象
        """
        # 步骤 1: 确保 .env 文件存在
        env_file_path = Path(".env")
        if not env_file_path.exists():
            # 如果 .env 文件不存在，复制 .env.example
            env_example_path = Path(".env.example")
            if env_example_path.exists():
                import shutil

                shutil.copy2(env_example_path, env_file_path)
                print_info("已从 .env.example 复制生成 .env 文件")

        # 步骤 2: 加载 .env 文件中的环境变量
        if env_file_path.exists():
            from dotenv import load_dotenv

            load_dotenv(env_file_path, override=True)
            print_info(f"已加载 .env 文件: {env_file_path}")

        # 步骤 3: 获取环境变量中指定的配置文件路径
        config_file_path = cls.get_env_config_file_path()
        print_info(f"配置文件路径: {config_file_path}")

        # 步骤 4: 从指定的配置文件加载设置
        if config_file_path.exists():
            # 如果配置文件存在，从文件加载
            import toml

            with open(config_file_path, encoding="utf-8") as f:
                config_data = toml.load(f)

            # 创建实例并应用配置文件中的设置
            settings = cls()
            if "log" in config_data:
                settings.log = LogSettings(**config_data["log"])
            if "download" in config_data:
                settings.download = DownloadSettings(**config_data["download"])
            if "login" in config_data:
                settings.login = LoginSettings(**config_data["login"])
            if "history" in config_data:
                settings.history = HistorySettings(**config_data["history"])
            if "network" in config_data:
                settings.network = NetworkSettings(**config_data["network"])

            # 在model_post_init中会设置login.default_output的正确值
            settings.model_post_init(None)

            env_cookie_file_path = settings.login.default_output
            print_info(f"cookie 默认的配置文件路径: {env_cookie_file_path}")

            print_info(f"已从配置文件加载设置: {config_file_path}")
            return settings
        else:
            # 如果配置文件不存在，使用默认设置并保存到指定位置
            settings = cls()
            # 确保配置文件目录存在
            config_file_path.parent.mkdir(parents=True, exist_ok=True)
            settings.save_to_file(str(config_file_path))
            print_info(f"已创建默认配置文件: {config_file_path}")
            return settings

    def save_to_file(self, config_file_path: str = None) -> None:
        """
        保存配置到文件

        Args:
            config_file_path: 配置文件路径，如果为None则使用默认路径
        """
        try:
            import toml

            if config_file_path is None:
                config_file = self.get_env_config_file_path()
            else:
                config_file = Path(config_file_path)

            # 确保配置目录存在
            config_file.parent.mkdir(parents=True, exist_ok=True)

            # 转换为字典并保存
            config_dict = {
                "log": self.log.model_dump(),
                "download": self.download.model_dump(),
                "login": self.login.model_dump(),
                "history": self.history.model_dump(),
                "network": self.network.model_dump(),
            }

            with open(config_file, "w", encoding="utf-8") as f:
                toml.dump(config_dict, f)

            print_info(f"配置已保存到: {config_file}")
        except Exception as e:
            # 如果保存失败，不抛出异常，但记录日志
            print_warning(f"无法将配置保存到文件: {e}")
