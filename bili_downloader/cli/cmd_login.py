import os

import typer

from bili_downloader.cli.global_config import env_bool
from bili_downloader.config.settings import Settings
from bili_downloader.utils.logger import logger
from bili_downloader.utils.print_utils import print_message

app = typer.Typer()


@app.command()
def login(
    method: str = typer.Option(
        "",
        "--method",
        "-m",
        help="登录方法 (qr为二维码扫描, web为浏览器登录)",
    ),
    output: str = typer.Option("", "--output", "-o", help="Cookie输出文件路径"),
    timeout: int = typer.Option(0, "--timeout", "-t", help="二维码登录超时时间(秒)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="启用详细日志"),
):
    """
    使用二维码扫描或网页浏览器登录Bilibili

    此命令提供两种登录Bilibili的方法:

    1. 二维码扫描 (默认): 生成一个二维码，您可以使用Bilibili手机应用扫描
    2. 网页浏览器: 在默认浏览器中打开Bilibili登录页面进行手动登录

    登录后，Cookie将保存到文件中，供下载命令使用。
    """
    try:
        # 从文件加载设置或创建默认设置
        settings = Settings.load_from_file()

        # 确定方法，优先级：命令行 > 环境变量 > 配置文件默认值 > "qr"
        # 方法默认值优先级：命令行 > 环境变量 > 配置文件默认值 > "qr"
        default_method = os.environ.get("LOGIN__DEFAULT_METHOD", "qr")
        login_method = method if method else default_method

        # 输出文件默认值优先级：命令行 > 环境变量 > 配置文件历史记录 > "cookie.txt"
        default_output = os.environ.get("LOGIN__DEFAULT_OUTPUT", "cookie.txt")
        output_file = output if output else default_output

        # 超时默认值优先级：命令行 > 环境变量 > 配置文件默认值 > 180
        default_timeout = int(os.environ.get("LOGIN__DEFAULT_TIMEOUT", "180"))
        timeout_value = timeout if timeout > 0 else default_timeout

        logger.info(
            f"Starting {login_method} login process",
            method=login_method,
            output=output_file,
            timeout=timeout_value,
        )

        # 创建二维码登录实例
        from bili_downloader.core.qrcode_login import QRCodeLogin

        qr_login = QRCodeLogin()

        # 根据方法执行登录
        if login_method.lower() == "qr":
            # 二维码登录
            cookie = qr_login.login_with_qr_code(timeout=timeout_value)
        elif login_method.lower() == "web":
            # 网页浏览器登录
            cookie = qr_login.login_with_browser()
            if cookie == "MANUAL_LOGIN_REQUIRED":
                # 对于网页登录，用户需要手动提供cookie
                print_message("\n请输入您的Bilibili cookie (从浏览器开发者工具获取):")
                cookie = input().strip()
        else:
            raise ValueError(f"未知登录方法: {login_method}。请使用 'qr' 或 'web'。")

        # 保存Cookie到文件
        qr_login.save_cookie_to_file(cookie, output_file)

        logger.info("登录成功，Cookie已保存")
        print_message(f"\n登录成功! Cookie已保存到 {output_file}")
        print_message("您现在可以使用此Cookie的下载命令了。")

    except KeyboardInterrupt:
        logger.info("用户中断了登录过程")
        print_message("\n登录过程被用户中断。")
    except Exception as e:
        logger.error("登录失败", error=str(e))
        print_message(f"\n登录失败: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
