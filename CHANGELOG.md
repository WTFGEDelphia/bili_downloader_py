# Changelog

## [0.4.2] - 2025-09-06

### Refactored

- 统一项目中的日志打印：使用rich替代所有print调用
- 创建统一的日志打印模块(utils/print_utils.py)提供一致的输出格式
- 移除了项目中所有直接使用print的地方，提高代码的一致性和可维护性

## [0.4.1] - 2025-09-06

### Refactored

- 重构全局配置逻辑：提取重复的配置代码到独立模块
- 创建全局配置管理模块(cli/global_config.py)统一处理日志、设置加载和Cookie管理
- 移除各命令模块中的重复配置代码，提高代码复用性和可维护性

## [0.4.0] - 2025-09-06

### Added

- 添加Bilibili搜索功能：支持综合搜索和分类搜索
- 新增search CLI命令：可搜索视频、番剧、用户等内容
- 实现WBI签名算法：支持Bilibili搜索接口的鉴权机制

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
