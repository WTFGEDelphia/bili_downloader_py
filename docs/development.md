# 开发指南

## 项目结构

```
bili_downloader_py/
├─ bili_downloader/     # 主包
│  ├─ __init__.py
│  ├─ core/             # 纯业务逻辑
│  ├─ cli/              # Typer CLI
│  └─ config/           # 配置管理
├─ tests/               # 测试
├─ docs/                # 文档
└─ pyproject.toml       # 项目配置
```

## 开发环境设置

1. 克隆项目:
   ```bash
   git clone https://github.com/WTFGEDelphia/bili_downloader_py.git
   cd bili_downloader_py
   ```

2. 创建虚拟环境:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # 或
   .venv\Scripts\activate  # Windows
   ```

3. 安装开发依赖:
   ```bash
   pip install -r requirements-dev.txt
   ```

## 代码格式化和检查

```bash
# 格式化代码
black .
isort .

# 代码检查
ruff check .

# 运行测试
pytest
```

## 添加新功能

1. 在 `bili_downloader/core/` 中实现核心逻辑
2. 在 `bili_downloader/cli/` 中添加 CLI 命令
3. 在 `tests/` 中添加测试用例
4. 更新文档