# Supertester Auto-Iterate

自动迭代优化 Supertester 插件的 skill 规则。

## Setup

使用 [uv](https://docs.astral.sh/uv/) 管理虚拟环境和依赖。

```bash
cd scripts/auto-iterate
uv venv                              # 创建 .venv (首次)
source .venv/Scripts/activate        # Git Bash
uv pip install -r requirements.txt   # 安装依赖
```

## Run

```bash
python orchestrator.py              # 首次或恢复
python orchestrator.py --status     # 查看进度
python orchestrator.py --phase 3    # 只跑 Phase 3
python orchestrator.py --module "URL通用校验"  # 只跑特定模块
```

详见 `docs/superpowers/specs/2026-04-12-auto-iterate-design.md`。
