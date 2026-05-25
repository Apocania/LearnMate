# LearnMate Seed Data

更新日期：2026-05-23

这里存放 LearnMate 本地开发和演示用的初始化数据说明。

当前演示数据脚本位于：

```bash
apps/api/scripts/seed_demo_data.py
```

在后端虚拟环境中执行：

```bash
cd apps/api
APP_ENV=development .venv/bin/python scripts/seed_demo_data.py
```

脚本会创建学生、伴学师、课程、章节、课件、讨论、消息、学习记录、AI 会话和头像等展示数据。重复执行会按固定演示账号更新数据，便于截图前快速恢复一个内容较完整的状态。
