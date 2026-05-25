# Git 开发与 GitHub 多人协作命令查询大全

更新日期：2026-05-23

> 适用于日常 Git 本地开发、分支管理、远程同步、Pull Request 协作、冲突处理、版本回退与发布流程。

## 目录

- [基础配置](#基础配置)
- [仓库初始化与克隆](#仓库初始化与克隆)
- [查看状态与历史](#查看状态与历史)
- [暂存与提交](#暂存与提交)
- [分支管理](#分支管理)
- [远程仓库](#远程仓库)
- [拉取与推送](#拉取与推送)
- [多人协作推荐流程](#多人协作推荐流程)
- [Pull Request 常用命令](#pull-request-常用命令)
- [合并与变基](#合并与变基)
- [冲突处理](#冲突处理)
- [撤销与回退](#撤销与回退)
- [临时保存工作区](#临时保存工作区)
- [标签与发布](#标签与发布)
- [GitHub CLI 常用命令](#github-cli-常用命令)
- [常见问题排查](#常见问题排查)
- [推荐别名](#推荐别名)
- [常用协作规范](#常用协作规范)

## 基础配置

### 查看配置

```bash
git config --list
git config --global --list
```

### 设置用户名和邮箱

```bash
git config --global user.name "你的名字"
git config --global user.email "your-email@example.com"
```

### 设置默认分支名

```bash
git config --global init.defaultBranch main
```

### 设置默认编辑器

```bash
git config --global core.editor "code --wait"
```

### 设置换行符

Windows 推荐：

```bash
git config --global core.autocrlf true
```

macOS / Linux 推荐：

```bash
git config --global core.autocrlf input
```

### 查看当前用户信息

```bash
git config user.name
git config user.email
```

## 仓库初始化与克隆

### 初始化本地仓库

```bash
git init
```

### 克隆远程仓库

```bash
git clone https://github.com/owner/repo.git
git clone git@github.com:owner/repo.git
```

### 克隆到指定目录

```bash
git clone https://github.com/owner/repo.git my-project
```

### 只克隆指定分支

```bash
git clone -b develop https://github.com/owner/repo.git
```

## 查看状态与历史

### 查看工作区状态

```bash
git status
git status -sb
```

### 查看提交历史

```bash
git log
git log --oneline
git log --oneline --graph --decorate --all
```

### 查看某个文件历史

```bash
git log -- path/to/file
git log -p -- path/to/file
```

### 查看最近一次提交

```bash
git show
```

### 查看指定提交

```bash
git show <commit-id>
```

### 查看文件修改差异

```bash
git diff
git diff path/to/file
```

### 查看已暂存的差异

```bash
git diff --staged
```

### 查看两个分支差异

```bash
git diff main..feature/login
```

### 查看每行代码最后是谁改的

```bash
git blame path/to/file
```

## 暂存与提交

### 添加文件到暂存区

```bash
git add path/to/file
git add .
git add -A
```

### 交互式暂存部分修改

```bash
git add -p
```

### 提交修改

```bash
git commit -m "feat: add login page"
```

### 跳过暂存直接提交已跟踪文件

```bash
git commit -am "fix: update user validation"
```

注意：`git commit -am` 不会提交新文件。

### 修改最近一次提交信息

```bash
git commit --amend
git commit --amend -m "fix: correct commit message"
```

### 向最近一次提交追加修改

```bash
git add .
git commit --amend --no-edit
```

如果该提交已经推送到远程，修改后通常需要强制推送，协作分支请谨慎操作。

## 分支管理

### 查看分支

```bash
git branch
git branch -a
git branch -r
```

### 创建分支

```bash
git branch feature/login
```

### 切换分支

```bash
git switch feature/login
```

旧命令：

```bash
git checkout feature/login
```

### 创建并切换分支

```bash
git switch -c feature/login
```

旧命令：

```bash
git checkout -b feature/login
```

### 从指定分支创建新分支

```bash
git switch main
git pull
git switch -c feature/login
```

### 重命名当前分支

```bash
git branch -m new-branch-name
```

### 删除本地分支

```bash
git branch -d feature/login
```

强制删除：

```bash
git branch -D feature/login
```

### 删除远程分支

```bash
git push origin --delete feature/login
```

### 查看本地分支与远程分支关联关系

```bash
git branch -vv
```

## 远程仓库

### 查看远程仓库

```bash
git remote -v
```

### 添加远程仓库

```bash
git remote add origin https://github.com/owner/repo.git
```

### 修改远程仓库地址

```bash
git remote set-url origin git@github.com:owner/repo.git
```

### 删除远程仓库

```bash
git remote remove origin
```

### 查看远程仓库详细信息

```bash
git remote show origin
```

## 拉取与推送

### 拉取远程最新代码

```bash
git pull
```

### 拉取指定分支

```bash
git pull origin main
```

### 获取远程更新但不自动合并

```bash
git fetch origin
```

### 推送当前分支

```bash
git push
```

### 第一次推送并建立 upstream

```bash
git push -u origin feature/login
```

之后可直接：

```bash
git push
git pull
```

### 推送到指定远程分支

```bash
git push origin feature/login
```

### 强制推送

```bash
git push --force-with-lease
```

不推荐使用：

```bash
git push --force
```

`--force-with-lease` 会在远程分支被他人更新时拒绝覆盖，更适合协作场景。

## 多人协作推荐流程

### 开始一个新功能

```bash
git switch main
git pull origin main
git switch -c feature/login
```

### 开发并提交

```bash
git status
git add .
git commit -m "feat: add login page"
```

### 推送分支

```bash
git push -u origin feature/login
```

### 创建 Pull Request

在 GitHub 页面创建，或使用 GitHub CLI：

```bash
gh pr create --base main --head feature/login --title "feat: add login page" --body "新增登录页面"
```

### PR 审查后更新分支

```bash
git add .
git commit -m "fix: address review comments"
git push
```

### PR 合并后清理本地分支

```bash
git switch main
git pull origin main
git branch -d feature/login
git fetch --prune
```

## Pull Request 常用命令

以下命令需要安装 GitHub CLI 并登录：

```bash
gh auth login
```

### 查看 PR 列表

```bash
gh pr list
```

### 查看当前分支关联的 PR

```bash
gh pr view
```

### 查看 PR 详情

```bash
gh pr view 123
```

### 创建 PR

```bash
gh pr create
gh pr create --base main --head feature/login
```

### 检出别人的 PR 到本地

```bash
gh pr checkout 123
```

### 查看 PR diff

```bash
gh pr diff 123
```

### 查看 PR 检查状态

```bash
gh pr checks 123
```

### 合并 PR

```bash
gh pr merge 123 --merge
gh pr merge 123 --squash
gh pr merge 123 --rebase
```

### 给 PR 添加评论

```bash
gh pr comment 123 --body "LGTM"
```

## 合并与变基

### 合并分支

```bash
git switch main
git merge feature/login
```

### 将 main 的最新代码合并到当前分支

```bash
git switch feature/login
git fetch origin
git merge origin/main
```

### 将当前分支变基到 main

```bash
git switch feature/login
git fetch origin
git rebase origin/main
```

### 继续 rebase

```bash
git rebase --continue
```

### 取消 rebase

```bash
git rebase --abort
```

### 合并和 rebase 如何选择

| 场景 | 推荐方式 |
| --- | --- |
| 共享分支、多人都在用 | `merge` |
| 自己的功能分支、未合并前整理历史 | `rebase` |
| 想保留完整分支合并记录 | `merge` |
| 想让提交历史更线性 | `rebase` |

重要原则：不要随意 rebase 已经被多人共同使用的公共分支。

## 冲突处理

### 发生冲突后查看状态

```bash
git status
```

### 查看冲突文件

```bash
git diff --name-only --diff-filter=U
```

### 手动编辑冲突文件

冲突标记通常长这样：

```text
<<<<<<< HEAD
当前分支内容
=======
合入分支内容
>>>>>>> feature/login
```

编辑后删除冲突标记，保留最终需要的内容。

### 标记冲突已解决

```bash
git add path/to/conflict-file
```

### 合并冲突后完成 merge

```bash
git commit
```

### rebase 冲突后继续

```bash
git rebase --continue
```

### 放弃本次 merge

```bash
git merge --abort
```

### 放弃本次 rebase

```bash
git rebase --abort
```

### 使用当前分支版本解决某个文件

```bash
git checkout --ours path/to/file
git add path/to/file
```

### 使用对方分支版本解决某个文件

```bash
git checkout --theirs path/to/file
git add path/to/file
```

注意：在 rebase 场景中，`ours` 和 `theirs` 的含义容易让人误解，使用前建议先确认文件内容。

## 撤销与回退

### 撤销工作区某个文件的修改

```bash
git restore path/to/file
```

### 撤销所有未暂存修改

```bash
git restore .
```

### 取消暂存某个文件

```bash
git restore --staged path/to/file
```

### 取消暂存所有文件

```bash
git restore --staged .
```

### 回退到上一个提交，但保留修改到工作区

```bash
git reset --soft HEAD~1
```

### 回退到上一个提交，保留修改但取消暂存

```bash
git reset --mixed HEAD~1
```

### 回退到上一个提交并丢弃修改

```bash
git reset --hard HEAD~1
```

危险：`reset --hard` 会丢弃本地修改，执行前请确认没有需要保留的内容。

### 回退到指定提交

```bash
git reset --hard <commit-id>
```

### 用新提交撤销某个提交

```bash
git revert <commit-id>
```

协作分支上更推荐 `revert`，因为它不会改写公共历史。

### 查看操作记录并找回误删提交

```bash
git reflog
git reset --hard <reflog-id>
```

## 临时保存工作区

### 保存当前未提交修改

```bash
git stash
```

### 保存并添加说明

```bash
git stash push -m "wip: login page"
```

### 包含未跟踪文件

```bash
git stash -u
```

### 查看 stash 列表

```bash
git stash list
```

### 恢复最近一次 stash

```bash
git stash pop
```

### 只应用但不删除 stash

```bash
git stash apply stash@{0}
```

### 删除某个 stash

```bash
git stash drop stash@{0}
```

### 清空所有 stash

```bash
git stash clear
```

## 标签与发布

### 查看标签

```bash
git tag
```

### 创建轻量标签

```bash
git tag v1.0.0
```

### 创建带说明的标签

```bash
git tag -a v1.0.0 -m "release v1.0.0"
```

### 推送指定标签

```bash
git push origin v1.0.0
```

### 推送所有标签

```bash
git push origin --tags
```

### 删除本地标签

```bash
git tag -d v1.0.0
```

### 删除远程标签

```bash
git push origin --delete v1.0.0
```

## GitHub CLI 常用命令

### 登录与状态

```bash
gh auth login
gh auth status
```

### 查看仓库

```bash
gh repo view
gh repo view owner/repo
```

### 创建仓库

```bash
gh repo create
```

### 克隆仓库

```bash
gh repo clone owner/repo
```

### 查看 issue

```bash
gh issue list
gh issue view 123
```

### 创建 issue

```bash
gh issue create --title "bug: login failed" --body "描述问题"
```

### 查看 workflow 运行记录

```bash
gh run list
gh run view
```

### 查看某次 workflow 日志

```bash
gh run view <run-id> --log
```

### 重新运行 workflow

```bash
gh run rerun <run-id>
```

## 常见问题排查

### 本地分支落后远程

```bash
git fetch origin
git status
git pull --rebase
```

### 推送被拒绝

常见原因：远程分支比本地更新。

```bash
git pull --rebase
git push
```

### 清理已删除的远程分支引用

```bash
git fetch --prune
```

### 查看哪些分支已经合并到 main

```bash
git switch main
git branch --merged
```

### 查看哪些分支还没合并到 main

```bash
git switch main
git branch --no-merged
```

### 忽略已经被 Git 跟踪的文件

如果文件已经被提交过，单独写入 `.gitignore` 不会让 Git 停止跟踪，需要：

```bash
git rm --cached path/to/file
git commit -m "chore: stop tracking generated file"
```

### 修改远程默认分支名后同步本地

```bash
git branch -m master main
git fetch origin
git branch -u origin/main main
git remote set-head origin -a
```

### 当前分支跟错远程分支

```bash
git branch --unset-upstream
git branch -u origin/feature/login
```

### 文件大小写改名在部分系统不生效

```bash
git mv oldname tmpname
git mv tmpname NewName
git commit -m "chore: rename file"
```

## 推荐别名

### 设置常用别名

```bash
git config --global alias.st "status -sb"
git config --global alias.co "switch"
git config --global alias.br "branch"
git config --global alias.cm "commit -m"
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.unstage "restore --staged"
```

### 使用别名

```bash
git st
git co feature/login
git br
git lg
```

## 常用协作规范

### 分支命名建议

| 类型 | 示例 |
| --- | --- |
| 新功能 | `feature/login` |
| 修复 bug | `fix/login-error` |
| 紧急修复 | `hotfix/payment-crash` |
| 重构 | `refactor/user-service` |
| 文档 | `docs/api-guide` |
| 测试 | `test/user-service` |
| 构建/依赖 | `chore/update-deps` |

### Commit Message 建议

常见格式：

```text
<type>: <description>
```

示例：

```bash
git commit -m "feat: add user login"
git commit -m "fix: handle empty password"
git commit -m "docs: update deployment guide"
git commit -m "refactor: simplify auth middleware"
```

常见类型：

| 类型 | 含义 |
| --- | --- |
| `feat` | 新功能 |
| `fix` | 修复 bug |
| `docs` | 文档 |
| `style` | 格式调整，不影响逻辑 |
| `refactor` | 重构 |
| `test` | 测试 |
| `chore` | 构建、依赖、工具等杂项 |
| `perf` | 性能优化 |
| `ci` | CI/CD 配置 |

### PR 协作建议

- 一个 PR 尽量只解决一个问题。
- 提交 PR 前先同步目标分支最新代码。
- PR 标题尽量清楚描述变更目的。
- PR 描述中说明改了什么、为什么改、如何验证。
- 不要在公共分支随意使用 `git push --force`。
- 合并前确认 CI 通过、冲突已解决、评审意见已处理。

### 日常安全习惯

- 执行 `reset --hard`、`clean -fd`、强制推送前先确认 `git status`。
- 不确定当前状态时先执行 `git status -sb`。
- 合并主分支前优先提交或 stash 当前修改。
- 公共分支出现问题时优先使用 `git revert`。
- 改写历史只建议用于自己的功能分支。

## 快速场景速查

### 我想开始写新功能

```bash
git switch main
git pull origin main
git switch -c feature/your-feature
```

### 我想提交当前修改

```bash
git status
git add .
git commit -m "feat: describe your change"
git push -u origin feature/your-feature
```

### 我想同步 main 最新代码到当前分支

```bash
git fetch origin
git rebase origin/main
```

或：

```bash
git fetch origin
git merge origin/main
```

### 我想撤销某个文件的本地修改

```bash
git restore path/to/file
```

### 我想取消刚刚的提交但保留代码

```bash
git reset --soft HEAD~1
```

### 我想撤销已经推送的提交

```bash
git revert <commit-id>
git push
```

### 我想查看是谁改了这行代码

```bash
git blame path/to/file
```

### 我想把当前工作先藏起来切分支

```bash
git stash push -m "wip"
git switch other-branch
```

恢复：

```bash
git stash pop
```
