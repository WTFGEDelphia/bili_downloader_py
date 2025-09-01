# Changelog

## [0.2.3] - 2025-09-01

### Fixed

- 优化下载逻辑：检查目标文件是否存在，如果存在则跳过下载和合并过程
- 检查音频和视频文件是否已存在，避免重复下载

## [0.2.2] - 2025-09-01

### Fixed

- 优化axel下载器：添加超时设置、重试机制和更多参数配置

## [0.2.1] - 2025-09-01

### Fixed

- 修复依赖问题：添加 pydantic-settings 依赖以解决 ModuleNotFoundError

## [0.2.0] - 2025-09-01

### Added

- 添加优先下载合并功能：下载完一个audio和video后立即创建合并任务
- 添加关键字检索能力：只下载文件名包含指定关键字的剧集
- 添加 --keyword/-k 命令行参数支持
- 添加关键字过滤测试用例

## [0.1.0] - 2025-08-26

### Added

- 重构项目结构，遵循 Python CLI + GUI 统一规则提示词
- 添加 Poetry 项目配置
- 添加 Typer CLI 支持
- 添加配置管理 (Pydantic Settings)
- 添加日志支持 (structlog)
- 添加测试框架 (pytest)
- 添加代码格式化和检查工具 (black, isort, ruff)
- 添加文档

### Changed

- 将核心下载逻辑移至 `bili_downloader.core` 模块
- 更新 README.md
- 移除旧的 main.py 实现

### Removed

- 移除旧的目录结构