import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing CLI import...")

    print("CLI modules imported successfully!")

    print("\nTesting Settings import...")
    from bili_downloader.config.settings import Settings

    print("Settings imported successfully!")

    print("\nTesting Settings.load_from_file()...")
    settings = Settings.load_from_file()
    print("Settings loaded successfully!")
    print(f"Default quality: {settings.download.default_quality}")
    print(f"Default downloader: {settings.download.default_downloader}")

    print("\nAll imports successful!")

except Exception as e:
    print(f"Error occurred: {e}")
    import traceback

    traceback.print_exc()
