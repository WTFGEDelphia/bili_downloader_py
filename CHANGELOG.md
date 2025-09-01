# Changelog

## [0.3.3] - 2025-09-01

### Fixed

- 完善配置文件支持：实现config.toml文件的自动创建和读取
- 添加toml依赖以支持配置文件序列化
- 优化Docker环境中的配置文件持久化支持

## [0.3.2] - 2025-09-01

### Fixed

- 修复Docker环境中cookie文件读取问题：支持多种cookie文件位置
- 改进Dockerfile和docker-compose.yml配置以更好地支持cookie文件挂载

## [0.3.1] - 2025-09-01

### Added

- 添加docker-compose.yml支持：提供Docker Compose配置文件
- 添加Docker Compose使用说明到README.md

## [0.3.0] - 2025-09-01

### Added

- 添加Docker支持：创建Dockerfile和.dockerignore文件
- 提供Docker使用说明和示例命令