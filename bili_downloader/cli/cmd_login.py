import typer
from pathlib import Path

from bili_downloader.core.qrcode_login import QRCodeLogin
from bili_downloader.utils.logger import logger


app = typer.Typer()


@app.command()
def login(
    method: str = typer.Option(
        "qr",
        "--method",
        "-m",
        help="Login method (qr for QR code scan, web for browser login)"
    ),
    output: str = typer.Option(
        "cookie.txt",
        "--output",
        "-o",
        help="Output file path for cookie"
    ),
    timeout: int = typer.Option(
        180,
        "--timeout",
        "-t",
        help="QR code login timeout in seconds"
    )
):
    """
    Login to Bilibili using QR code scan or web browser
    
    This command provides two methods to log in to Bilibili:
    
    1. QR code scan (default): Generates a QR code that you can scan with your Bilibili mobile app
    2. Web browser: Opens the Bilibili login page in your default browser for manual login
    
    After logging in, the cookie will be saved to a file for use with the download command.
    """
    try:
        logger.info(f"Starting {method} login process")
        
        # Create QR code login instance
        qr_login = QRCodeLogin()
        
        # Perform login based on method
        if method.lower() == "qr":
            # QR code login
            cookie = qr_login.login_with_qr_code(timeout=timeout)
        elif method.lower() == "web":
            # Web browser login
            cookie = qr_login.login_with_browser()
            if cookie == "MANUAL_LOGIN_REQUIRED":
                # For web login, user needs to manually provide cookie
                print("\nPlease enter your Bilibili cookie (obtained from browser developer tools):")
                cookie = input().strip()
        else:
            raise ValueError(f"Unknown login method: {method}. Use 'qr' or 'web'.")
        
        # Save cookie to file
        qr_login.save_cookie_to_file(cookie, output)
        
        logger.info("Login successful and cookie saved")
        print(f"\nLogin successful! Cookie saved to {output}")
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