import json
import time
import webbrowser
from typing import Optional, Tuple
from urllib.parse import urlparse

import requests

from bili_downloader.utils.logger import logger


class QRCodeLogin:
    """Bilibili QR Code Login Class"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": "https://www.bilibili.com/",
            }
        )

    def generate_qr_code(self) -> Tuple[str, str]:
        """
        Generate QR code for login

        Returns:
            Tuple[str, str]: (qr_url, qrcode_key)
        """
        url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            if data.get("code") == 0:
                qr_url = data["data"]["url"]
                qrcode_key = data["data"]["qrcode_key"]
                logger.info("QR code generated successfully")
                return qr_url, qrcode_key
            else:
                logger.error(
                    "Failed to generate QR code",
                    code=data.get("code"),
                    message=data.get("message"),
                )
                raise Exception(f"Failed to generate QR code: {data.get('message')}")

        except requests.RequestException as e:
            logger.error("Network error when generating QR code", error=str(e))
            raise Exception(f"Network error when generating QR code: {e}")
        except json.JSONDecodeError as e:
            logger.error("Failed to parse QR code response", error=str(e))
            raise Exception(f"Failed to parse QR code response: {e}")

    def display_qr_code(self, qr_url: str) -> None:
        """
        Display QR code in terminal using qrcode library

        Args:
            qr_url (str): The QR code URL to display
        """
        try:
            import sys
            from io import StringIO

            import qrcode

            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=1,
                border=1,
            )

            # Add data and make QR code
            qr.add_data(qr_url)
            qr.make(fit=True)

            # Print QR code to terminal
            qr.print_ascii(out=sys.stdout, invert=True)

        except ImportError:
            # If qrcode library is not available, just print the URL
            print(f"QR Code URL: {qr_url}")
            print("Please visit this URL or scan it with your Bilibili mobile app")
        except Exception as e:
            logger.warning("Failed to generate QR code display", error=str(e))
            print(f"QR Code URL: {qr_url}")
            print("Please visit this URL or scan it with your Bilibili mobile app")

    def poll_qr_login(self, qrcode_key: str) -> Optional[str]:
        """
        Poll for QR code login status

        Args:
            qrcode_key (str): The QR code key

        Returns:
            Optional[str]: Cookie string if login successful, None otherwise
        """
        url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
        params = {"qrcode_key": qrcode_key}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            code = data["data"]["code"]
            message = data["data"]["message"]

            if code == 86101:
                # Not scanned yet
                logger.debug("QR code not scanned yet")
                return None
            elif code == 86090:
                # Scanned but not confirmed
                logger.info("QR code scanned, please confirm on mobile device")
                return None
            elif code == 86038:
                # QR code expired
                logger.error("QR code expired")
                raise Exception("QR code expired, please try again")
            elif code == 0:
                # Login successful
                logger.info("Login successful")

                # Extract cookies from session
                cookies = self.session.cookies
                cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])

                return cookie_str
            else:
                logger.error("Unknown login status", code=code, message=message)
                raise Exception(f"Unknown login status: {code} - {message}")

        except requests.RequestException as e:
            logger.error("Network error when polling QR login", error=str(e))
            raise Exception(f"Network error when polling QR login: {e}")
        except json.JSONDecodeError as e:
            logger.error("Failed to parse QR login response", error=str(e))
            raise Exception(f"Failed to parse QR login response: {e}")

    def login_with_qr_code(self, timeout: int = 180) -> str:
        """
        Login with QR code

        Args:
            timeout (int): Timeout in seconds (default: 180)

        Returns:
            str: Cookie string
        """
        # Generate QR code
        qr_url, qrcode_key = self.generate_qr_code()

        # Display QR code in terminal
        print("Please scan the following QR code with your Bilibili mobile app:")
        self.display_qr_code(qr_url)
        print("\nIf you can't scan the QR code, please visit this URL manually:")
        print(f"{qr_url}")
        print("\nWaiting for scan and confirmation on your mobile device...")

        # Poll for login status
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                cookie = self.poll_qr_login(qrcode_key)
                if cookie:
                    return cookie
            except Exception as e:
                if "expired" in str(e).lower():
                    # QR code expired, generate a new one
                    print("\nQR code expired, generating a new one...")
                    qr_url, qrcode_key = self.generate_qr_code()
                    print("Please scan the new QR code with your Bilibili mobile app:")
                    self.display_qr_code(qr_url)
                    print(
                        "\nIf you can't scan the QR code, please visit this URL manually:"
                    )
                    print(f"{qr_url}")
                    print(
                        "\nWaiting for scan and confirmation on your mobile device..."
                    )
                    start_time = time.time()  # Reset timeout
                else:
                    raise e

            # Wait before polling again
            time.sleep(3)

        raise Exception("Login timeout, please try again")

    def login_with_browser(self) -> str:
        """
        Login by opening Bilibili login page in default browser

        Returns:
            str: Instructions for user to manually obtain cookies
        """
        # Bilibili main page URL
        login_url = "https://www.bilibili.com/"

        print("Opening Bilibili login page in your default browser...")
        print("Please log in to your Bilibili account in the browser that opens.")
        print("After logging in, follow these steps to get your cookies:")
        print("\n1. Open browser's developer tools (F12)")
        print("2. Go to the Network tab")
        print("3. Refresh the page")
        print("4. Find any request to bilibili.com")
        print("5. Right-click and select 'Copy' > 'Copy Request Headers'")
        print("6. Extract the 'Cookie' value from the headers")
        print("7. Save the cookie value to a file")
        print("\nPress Enter to continue and open the browser...")
        input()

        # Try to open the URL in the default browser
        try:
            webbrowser.open(login_url)
        except Exception as e:
            logger.warning("Failed to open browser", error=str(e))
            print(
                f"Failed to open browser automatically. Please visit {login_url} manually."
            )

        # Provide instructions for manual cookie extraction
        instructions = f"""
Manual Cookie Extraction Instructions:
=====================================

1. After logging in to Bilibili in your browser, open the developer tools (F12)
2. Go to the Network tab
3. Refresh the page (F5)
4. Find any request to bilibili.com (usually the first one)
5. Click on the request, then go to the Headers tab
6. Find the 'Cookie' header in the Request Headers section
7. Copy the entire cookie value
8. Save it to a file with the following format:

Example cookie.txt content:
----------------------------
SESSDATA=your_sessdata_value; bili_jct=your_bili_jct_value; DedeUserID=your_dedeuserid_value
----------------------------

Press Enter when you have saved your cookie to continue...
"""
        print(instructions)
        input()

        # For browser-based login, we can't automatically extract cookies
        # Return a placeholder that indicates manual intervention is needed
        return "MANUAL_LOGIN_REQUIRED"

    def save_cookie_to_file(
        self, cookie_str: str, filepath: str = "cookie.txt"
    ) -> None:
        """
        Save cookie to file

        Args:
            cookie_str (str): Cookie string
            filepath (str): File path to save cookie (default: "cookie.txt")
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(cookie_str)
            logger.info(f"Cookie saved to {filepath}")
        except Exception as e:
            logger.error("Failed to save cookie to file", error=str(e))
            raise Exception(f"Failed to save cookie to file: {e}")
