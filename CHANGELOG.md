# Changelog

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