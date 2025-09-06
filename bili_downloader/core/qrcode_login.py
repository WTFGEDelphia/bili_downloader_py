import json
import time
import webbrowser

import requests

from bili_downloader.utils.logger import logger
from bili_downloader.utils.print_utils import print_message


class QRCodeLogin:
    """Bilibili 二维码登录类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": "https://www.bilibili.com/",
            }
        )

    def generate_qr_code(self) -> tuple[str, str]:
        """
        生成登录二维码

        Returns:
            Tuple[str, str]: (二维码URL, 二维码key)
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
                    "生成二维码失败",
                    code=data.get("code"),
                    message=data.get("message"),
                )
                raise Exception(f"Failed to generate QR code: {data.get('message')}")

        except requests.RequestException as e:
            logger.error("Network error when generating QR code", error=str(e))
            raise Exception(f"生成二维码时网络错误: {e}")
        except json.JSONDecodeError as e:
            logger.error("Failed to parse QR code response", error=str(e))
            raise Exception(f"解析二维码响应失败: {e}")

    def display_qr_code(self, qr_url: str) -> None:
        """
        在终端中使用qrcode库显示二维码

        Args:
            qr_url (str): 要显示的二维码URL
        """
        try:
            import sys
            from io import StringIO

            import qrcode

            # 创建二维码实例
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=1,
                border=1,
            )

            # 添加数据并生成二维码
            qr.add_data(qr_url)
            qr.make(fit=True)

            # 在终端中打印二维码
            qr.print_ascii(out=sys.stdout, invert=True)

        except ImportError:
            # 如果qrcode库不可用，则只打印URL
            print_message(f"二维码URL: {qr_url}")
            print_message("请访问此URL或使用哔哩哔哩手机应用扫描")
        except Exception as e:
            logger.warning("Failed to display QR code", error=str(e))
            print_message(f"二维码URL: {qr_url}")
            print_message("请访问此URL或使用哔哩哔哩手机应用扫描")

    def poll_qr_login(self, qrcode_key: str) -> str | None:
        """
        轮询二维码登录状态

        Args:
            qrcode_key (str): 二维码key

        Returns:
            Optional[str]: 登录成功时返回Cookie字符串，否则返回None
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
                logger.error("QR code has expired")
                raise Exception("二维码已过期，请重试")
            elif code == 0:
                # Login successful
                logger.info("Login successful")

                # Extract cookies from session
                cookies = self.session.cookies
                cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])

                return cookie_str
            else:
                logger.error("Unknown login status", code=code, message=message)
                raise Exception(f"未知登录状态: {code} - {message}")

        except requests.RequestException as e:
            logger.error("Network error when polling QR login", error=str(e))
            raise Exception(f"轮询二维码登录时网络错误: {e}")
        except json.JSONDecodeError as e:
            logger.error("Failed to parse QR login response", error=str(e))
            raise Exception(f"解析二维码登录响应失败: {e}")

    def login_with_qr_code(self, timeout: int = 180) -> str:
        """
        使用二维码登录

        Args:
            timeout (int): 超时时间(秒) (默认: 180)

        Returns:
            str: Cookie字符串
        """
        # 生成二维码
        qr_url, qrcode_key = self.generate_qr_code()

        # 在终端中显示二维码
        print_message("请使用哔哩哔哩手机应用扫描以下二维码：")
        self.display_qr_code(qr_url)
        print_message("\n如果您无法扫描二维码，请手动访问以下URL：")
        print_message(f"{qr_url}")
        print_message("\n等待您在移动设备上扫描和确认...")

        # 轮询登录状态
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                cookie = self.poll_qr_login(qrcode_key)
                if cookie:
                    return cookie
            except Exception as e:
                if "expired" in str(e).lower():
                    # 二维码已过期，生成新的
                    print_message("\n二维码已过期，正在生成新的二维码...")
                    qr_url, qrcode_key = self.generate_qr_code()
                    print_message("请使用哔哩哔哩手机应用扫描新的二维码：")
                    self.display_qr_code(qr_url)
                    print_message("\n如果您无法扫描二维码，请手动访问以下URL：")
                    print_message(f"{qr_url}")
                    print_message("\n请在移动设备上扫描和确认...")
                    start_time = time.time()  # 重置超时
                else:
                    raise e

            # 轮询前等待
            time.sleep(3)

        raise Exception("登录超时，请重试")

    def login_with_browser(self) -> str:
        """
        通过在默认浏览器中打开Bilibili登录页面进行登录

        Returns:
            str: 指示用户手动获取cookies的说明
        """
        # Bilibili主页URL
        login_url = "https://www.bilibili.com/"

        print_message("正在默认浏览器中打开哔哩哔哩登录页面...")
        print_message("请在打开的浏览器中登录您的哔哩哔哩账户。")
        print_message("登录后，请按照以下步骤获取您的Cookie：")
        print_message("\n1. 打开浏览器的开发者工具 (F12)")
        print_message("2. 转到Network标签页")
        print_message("3. 刷新页面")
        print_message("4. 找到任何到bilibili.com的请求")
        print_message("5. 右键单击并选择'Copy' > 'Copy Request Headers'")
        print_message("6. 从头部信息中提取'Cookie'值")
        print_message("7. 将Cookie值保存到文件中")
        print_message("\n按Enter键继续并打开浏览器...")
        input()

        # 尝试在默认浏览器中打开URL
        try:
            webbrowser.open(login_url)
        except Exception as e:
            logger.warning("Failed to open browser", error=str(e))
            print_message("打开浏览器失败，请手动访问以下URL：")

        # 提供手动提取cookie的说明
        instructions = """
手动提取Cookie说明:
=====================================

1. 在浏览器中登录Bilibili后，打开开发者工具 (F12)
2. 转到Network标签页
3. 刷新页面 (F5)
4. 找到任何到bilibili.com的请求 (通常是第一个)
5. 点击该请求，然后转到Headers标签页
6. 在Request Headers部分找到'Cookie'头
7. 复制整个cookie值
8. 以以下格式保存到文件中:

示例 cookie.txt 内容:
----------------------------
SESSDATA=your_sessdata_value; bili_jct=your_bili_jct_value; DedeUserID=your_dedeuserid_value
----------------------------

保存好cookie后按Enter键继续...
"""
        print_message(instructions)
        input()

        # 对于基于浏览器的登录，我们无法自动提取cookies
        # 返回一个占位符，表示需要手动干预
        return "MANUAL_LOGIN_REQUIRED"

    def save_cookie_to_file(
        self, cookie_str: str, filepath: str = "cookie.txt"
    ) -> None:
        """
        保存cookie到文件

        Args:
            cookie_str (str): Cookie字符串
            filepath (str): 保存cookie的文件路径 (默认: "cookie.txt")
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(cookie_str)
            logger.info(f"Cookie saved to {filepath}")
        except Exception as e:
            logger.error("Failed to save cookie to file", error=str(e))
            raise Exception(f"保存cookie到文件失败: {e}")
