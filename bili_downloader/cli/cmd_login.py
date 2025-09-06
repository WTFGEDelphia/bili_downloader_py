import os
from pathlib import Path

import typer

from bili_downloader.config.settings import Settings
from bili_downloader.core.qrcode_login import QRCodeLogin
from bili_downloader.utils.logger import configure_logger, logger

app = typer.Typer()


def env_bool(key: str, default: bool = False) -> bool:
    """把环境变量 key 解析为 bool；未设置或空串返回 default。"""
    val = os.environ.get(key, "").strip().lower()
    if val in {"1", "true", "yes", "on"}:
        return True
    if val in {"0", "false", "no", "off", ""}:
        return False
    # 如果值既不是上面任何一项，就按 Python 的 bool 语义兜底
    return bool(val)


@app.command()
def login(
    method: str = typer.Option(
        "",
        "--method",
        "-m",
        help="Login method (qr for QR code scan, web for browser login)",
    ),
    output: str = typer.Option(
        "", "--output", "-o", help="Output file path for cookie"
    ),
    timeout: int = typer.Option(
        0, "--timeout", "-t", help="QR code login timeout in seconds"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    """
    Login to Bilibili using QR code scan or web browser

    This command provides two methods to log in to Bilibili:

    1. QR code scan (default): Generates a QR code that you can scan with your Bilibili mobile app
    2. Web browser: Opens the Bilibili login page in your default browser for manual login

    After logging in, the cookie will be saved to a file for use with the download command.
    """
    # Configure logger
    configure_logger(verbose)

    try:
        # Load settings from file or create default
        settings = Settings.load_from_file()

        # Determine method with environment variable and default fallback
        # Method default value priority: command line > environment variable > config file default > "qr"
        default_method = os.environ.get("LOGIN__DEFAULT_METHOD", "qr")
        login_method = method if method else default_method

        # Output file default value priority: command line > environment variable > config file history > "cookie.txt"
        default_output = os.environ.get("LOGIN__DEFAULT_OUTPUT", "cookie.txt")
        output_file = output if output else default_output

        # Timeout default value priority: command line > environment variable > config file default > 180
        default_timeout = int(os.environ.get("LOGIN__DEFAULT_TIMEOUT", "180"))
        timeout_value = timeout if timeout > 0 else default_timeout

        logger.info(
            f"Starting {login_method} login process",
            method=login_method,
            output=output_file,
            timeout=timeout_value,
        )

        # Create QR code login instance
        qr_login = QRCodeLogin()

        # Perform login based on method
        if login_method.lower() == "qr":
            # QR code login
            cookie = qr_login.login_with_qr_code(timeout=timeout_value)
        elif login_method.lower() == "web":
            # Web browser login
            cookie = qr_login.login_with_browser()
            if cookie == "MANUAL_LOGIN_REQUIRED":
                # For web login, user needs to manually provide cookie
                print(
                    "\nPlease enter your Bilibili cookie (obtained from browser developer tools):"
                )
                cookie = input().strip()
        else:
            raise ValueError(
                f"Unknown login method: {login_method}. Use 'qr' or 'web'."
            )

        # Save cookie to file
        qr_login.save_cookie_to_file(cookie, output_file)

        logger.info("Login successful and cookie saved")
        print(f"\nLogin successful! Cookie saved to {output_file}")
        print("You can now use the download command with this cookie.")

    except KeyboardInterrupt:
        logger.info("Login process interrupted by user")
        print("\nLogin process interrupted by user.")
    except Exception as e:
        logger.error("Login failed", error=str(e))
        print(f"\nLogin failed: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
