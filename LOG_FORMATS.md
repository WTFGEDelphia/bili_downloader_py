# 多种日志格式支持

## 功能概述

本项目支持多种日志格式，以适应不同的使用场景和需求：

1. **JSON格式** (默认): 结构化日志，便于机器解析和处理
2. **控制台格式**: 带颜色的可读格式，适合开发和调试
3. **键值对格式**: 简洁的键值对形式，适合人类阅读
4. **简单文本格式**: 最基础的文本格式

## 格式详情

### 1. JSON 格式 (json)

**特点**: 结构化的JSON格式，便于机器解析和日志分析工具处理

**示例**:
```json
{"event": "开始下载", "logger": "downloader", "level": "info", "timestamp": "2025-09-06T10:30:45.123456Z"}
{"url": "https://example.com", "event": "下载完成", "logger": "downloader", "level": "info", "timestamp": "2025-09-06T10:30:50.654321Z"}
```

**适用场景**:
- 生产环境日志收集
- 与ELK、Splunk等日志分析平台集成
- 自动化监控和告警系统

### 2. 控制台格式 (console)

**特点**: 带颜色和格式化的控制台输出，便于人工阅读

**示例**:
```
2025-09-06 10:30:45 [info     ] 开始下载                         logger=downloader
2025-09-06 10:30:50 [info     ] 下载完成                         logger=downloader url=https://example.com
```

**适用场景**:
- 开发和调试阶段
- 本地运行时的人工监控
- 终端直接查看日志

### 3. 键值对格式 (keyvalue)

**特点**: 以键值对形式展示日志信息，简洁明了

**示例**:
```
timestamp='2025-09-06T10:30:45.123456Z' level='info' logger='downloader' event='开始下载'
timestamp='2025-09-06T10:30:50.654321Z' level='info' logger='downloader' event='下载完成' url='https://example.com'
```

**适用场景**:
- 需要简洁日志格式的环境
- 介于结构化和文本之间的平衡
- 简单的日志分析

### 4. 简单文本格式 (simple)

**特点**: 最基础的纯文本格式，去除所有额外装饰

**示例**:
```
2025-09-06 10:30:45 [info     ] 开始下载
2025-09-06 10:30:50 [info     ] 下载完成
```

**适用场景**:
- 对日志大小有严格要求的环境
- 简单的日志记录需求
- 与其他系统集成时的基础格式

## 使用方法

### CLI 命令行选项

```bash
# 使用默认的JSON格式
bili-downloader --log-to-file download

# 指定控制台格式
bili-downloader --log-to-file --log-format console download

# 指定键值对格式
bili-downloader --log-to-file --log-format keyvalue download

# 指定简单文本格式
bili-downloader --log-to-file --log-format simple download

# 使用短选项
bili-downloader -l -f json download
bili-downloader -l -f console download
bili-downloader -l -f keyvalue download
bili-downloader -l -f simple download
```

### 配置文件设置

在 `config.toml` 中配置默认日志格式：

```toml
[log]
enable_file_logging = true
log_file_path = "logs/bili_downloader.log"
log_level = "INFO"
log_format = "json"  # 支持: json, console, keyvalue, simple
max_log_file_size = 10485760  # 10MB
backup_count = 5
```

## 选择建议

1. **生产环境**: 推荐使用 `json` 格式，便于日志收集和分析
2. **开发调试**: 推荐使用 `console` 格式，便于阅读和调试
3. **简单记录**: 推荐使用 `keyvalue` 或 `simple` 格式，减小日志体积
4. **混合使用**: 可以在不同环境下使用不同格式，满足不同需求