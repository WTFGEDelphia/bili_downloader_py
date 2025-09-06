# 日志输出到文件功能说明

## 功能概述

本项目现已支持将日志同时输出到控制台和文件，具有以下特性：

1. **可配置性**：通过配置文件启用或禁用文件日志
2. **自动轮转**：当日志文件达到指定大小时自动创建新文件
3. **保留备份数量**：自动清理旧的日志文件，只保留指定数量的备份
4. **UTF-8编码**：支持中文日志内容
5. **CLI选项**：可通过命令行选项启用文件日志

## 配置说明

### 配置文件设置

在配置文件中添加以下设置以启用文件日志：

```toml
[log]
enable_file_logging = true
log_file_path = "logs/bili_downloader.log"
log_level = "INFO"
max_log_file_size = 10485760  # 10MB
backup_count = 5
```

### CLI使用

使用 `--log-to-file` 或 `-l` 选项启用文件日志：

```bash
# 启用文件日志并显示帮助
bili-downloader --log-to-file --help

# 启用文件日志并执行下载
bili-downloader --log-to-file download --url "https://www.bilibili.com/bangumi/play/ep123456"

# 启用详细日志和文件日志
bili-downloader --verbose --log-to-file login
```

## 技术实现

### 主要组件

1. **配置模型** (`config/settings.py`)：
   - 新增 `LogSettings` 类管理日志配置
   - 在 `Settings` 类中集成日志设置

2. **日志配置** (`utils/logger.py`)：
   - 修改 `configure_logger` 函数支持文件日志
   - 使用 `RotatingFileHandler` 实现日志轮转
   - 支持配置日志级别、文件路径等参数

3. **CLI集成** (`cli/main.py`)：
   - 添加 `--log-to-file` 全局选项
   - 在主回调函数中处理文件日志启用逻辑

### 日志格式

文件中的日志采用标准格式：
```
2025-09-07 00:34:40,008 - bili_downloader.cli.global_config - INFO - {"event": "这是普通信息", "info_value": "test_info", ...}
```

## 文件结构

日志文件默认保存在项目根目录的 `logs` 子目录中：
```
project_root/
├── logs/
│   ├── bili_downloader.log      # 当前日志文件
│   ├── bili_downloader.log.1    # 备份日志文件1
│   └── bili_downloader.log.2    # 备份日志文件2
└── ...
```

## 使用建议

1. **生产环境**：建议启用文件日志以便排查问题
2. **开发环境**：可根据需要选择是否启用文件日志
3. **日志级别**：根据需要调整日志级别（DEBUG/INFO/WARNING/ERROR）
4. **文件大小**：合理设置最大文件大小和备份数量以节省磁盘空间