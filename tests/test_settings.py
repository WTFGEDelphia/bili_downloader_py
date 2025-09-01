import os
import tempfile
from pathlib import Path

# 测试当前的Settings实现
try:
    from bili_downloader.config.settings import Settings
    
    # 创建临时目录进行测试
    with tempfile.TemporaryDirectory() as temp_dir:
        # 保存原始方法
        original_get_config_dir = Settings.get_config_dir
        
        # 临时修改配置目录
        Settings.get_config_dir = lambda: Path(temp_dir) / "config"
        
        try:
            print("Testing Settings.load_from_file()...")
            settings = Settings.load_from_file()
            print("Settings loaded successfully!")
            print(f"Default quality: {settings.download.default_quality}")
            print(f"Default downloader: {settings.download.default_downloader}")
            
            # 测试保存功能
            print("\nTesting Settings.save_to_file()...")
            settings.save_to_file()
            config_file = Settings.get_config_file()
            print(f"Config file created at: {config_file}")
            if config_file.exists():
                print("Config file exists!")
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print("Config file content:")
                    print(content)
            else:
                print("Config file does not exist!")
                
        finally:
            # 恢复原始方法
            Settings.get_config_dir = original_get_config_dir
            
    print("\nAll tests passed!")
    
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()