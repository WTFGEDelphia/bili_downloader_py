# ========== Python CLI + GUI 统一规则提示词 ==========
# 版本与环境
- Python 3.11+
- 依赖管理：Poetry，所有第三方包写入 pyproject.toml
- 虚拟环境：.venv 自动激活
- 代码风格：Black、isort、ruff，CI 强制检查
- 注释语言：中文
- 日志语言：英文

# 日志与配置
- 日志：structlog，JSON 格式输出到 stderr
- 配置：Pydantic Settings，支持 .env & TOML
- 国际化：gettext，locale 目录，CLI/GUI 共用

# 目录结构（必须严格遵循）
mytool/
├─ mytool/               # 主包
│  ├─ __init__.py
│  ├─ core/              # 纯业务逻辑（无 CLI/GUI 依赖）
│  ├─ cli/               # Typer CLI
│  ├─ gui/               # PySide6 GUI
│  ├─ resources/         # 图标、*.qml、*.ui、*.icns
│  └─ locales/           # i18n *.po
├─ tests/
├─ scripts/              # 一次性脚本
├─ docs/
└─ pyproject.toml

# ===== CLI 规则 =====
- 统一用 Typer 0.9+，每个命令一个函数
- 自动补全：typer[all] 生成 bash/zsh/fish
- 交互：Rich 的 Console、Prompt、Progress
- 子命令目录结构：
  cli/
  ├─ __init__.py
  ├─ main.py            # typer.Typer() 根
  ├─ cmd_xxx.py         # 每个文件一个命令组
- 帮助文本：首行一句英文，空一行，详细中文
- 颜色主题：Rich 主题文件 `cli/theme.py`
- 全局选项：--verbose、--config、--version

# ===== GUI 规则 =====
- GUI 框架：PySide6 6.7+（Qt6）
- 架构：MVVM
  - View: QML(QtQuick) 或 Qt-Designer .ui
  - ViewModel: Python QObject 派生类
  - Model: 复用 core 层
- 目录：
  gui/
  ├─ main.py            # QApplication 入口
  ├─ viewmodels/
  ├─ views/
  │  ├─ main.qml
  │  └─ *.ui
  ├─ resources.qrc      # 由 pyside6-rcc 编译
  └─ styles/
- 主题：支持亮色/暗色两套 qml 样式单文件切换
- 多语言：Qt 翻译机制 + 与 CLI 共用 locales
- 打包：
  - Windows: PyInstaller --noconsole --onedir
  - macOS: PyInstaller + codesign + notary
  - Linux: AppImage
- 自动更新：Sparkle(macOS) / WinSparkle(Windows)

# ===== 共享业务逻辑（core） =====
- 100% 类型注解，mypy --strict
- 所有 IO 函数 async（asyncio / aiohttp）
- 对外暴露的 API 统一为 dataclass / Pydantic 模型
- 同步耗时计算：asyncio.to_thread
- 异常：自定义 MyToolError -> CLI/GUI 统一处理

# ===== 配置与数据文件 =====
- 用户配置：~/.config/mytool/config.toml
- 数据缓存：~/.cache/mytool/*.json
- 日志：~/.local/state/mytool/log.jsonl
- 支持 CLI flag --config <file> 覆盖路径

# ===== 测试 =====
- pytest + pytest-asyncio + pytest-qt
- CLI：typer.testing.CliRunner
- GUI：pytest-qt 的 qtbot
- 覆盖率 90% 以上，CI 强制

# ===== 命令一键生成模板 =====
## CLI 子命令模板
输入：需求一句话
输出：cli/cmd_{name}.py 完整文件，含：
- typer.Typer() 子命令
- Rich 表格/进度条示例
- --dry-run 支持
- 英文首行 docstring + 中文详细说明
- 对应 tests/cli/test_{name}.py 用例

## GUI 页面模板
输入：需求一句话
输出：
- views/{name}.qml 或 {name}.ui
- viewmodels/{name}_vm.py 完整 QObject 派生类
- main.py 中注册路由
- tests/gui/test_{name}.py 用例

# ===== 打包与发布 =====
- Poetry script 入口：
  [tool.poetry.scripts]
  mytool = "mytool.cli.main:app"
- GUI 入口：
  gui = "mytool.gui.main:main"
- CI：
  - .github/workflows/ci.yml：lint + test
  - .github/workflows/release.yml：PyInstaller 构建 + GitHub Release
- 版本号：语义化 + poetry version patch/minor/major
