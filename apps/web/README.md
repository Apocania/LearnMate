# LearnMate Web

更新日期：2026-05-25

LearnMate 的 React + TypeScript + Vite 前端应用。

## Development

```bash
npm install
cp .env.example .env
npm run dev
```

访问：

```text
http://localhost:5173
```

## Build

```bash
npm run build
```

当前路由页面使用 `React.lazy` 和 `Suspense` 懒加载，构建后会按页面拆分 chunk。

当前界面已经调整为面向儿童学习场景的明亮风格，包含彩色背景、活泼卡片、顶部品牌动效、智能伴学示例对话和适合截图展示的首页内容。课程创建、课程编辑、详情模块和个人中心已强化对齐、悬停反馈、轻量跳转动效和中文显示。

## Main Pages

- `/login`：登录和注册，注册时可选择学生或伴学师，包含确认密码和用户名规则提示。
- `/courses`：课程中心。游客和学生只看到已发布课程；学生可加入/退出课程；伴学师可查看自己创建的草稿，编辑、删除自己的课程，并进入课件管理。
- `/courses/new`：独立创建课程页。伴学师可填写标题、介绍和发布状态，创建后进入课程详情继续维护章节、课件和学生名单。
- `/courses/:courseId`：课程详情。展示真实课程信息、选课人数、章节目录和绑定课件；学生可加入/退出，课程作者可维护章节、上传课件并管理学生名单。
- `/forum`：讨论交流。游客可浏览；支持课程筛选、关键词搜索和分页；帖子列表不展示附带标签；登录用户可展开评论区直接评论和点赞，并删除自己的评论；伴学师可隐藏、恢复、删除帖子和评论。
- `/forum/new`：独立发帖页。支持标题、Markdown 正文编辑/实时预览和最多 5 个附件上传。
- `/files`：文件资料。游客和学生可浏览/下载；伴学师可按课程/章节上传课件，并删除自己上传的课件。
- `/assistant`：智能伴学。登录后可选择课程资料并向后端发送问题，回答会展示引用来源。
- `/messages`：消息中心。学生可查看点赞、评论、私信、公告提醒；伴学师可发送私信和公告。
- `/reports/me`：个人中心。学生展示学习报告；伴学师展示教学看板，包括课程建设、学生参与、章节资料、课程概览和教学建议。

## API Client Behavior

`src/api/client.ts` 会统一处理请求：

- 从 `VITE_API_BASE_URL` 读取后端 API 地址。
- 自动附加 `learnmate_access_token`。
- 上传 `FormData` 时不强制设置 JSON header。
- 遇到 `401` 会清除本地登录信息并跳转 `/login`。
- 支持 `204 No Content` 和空响应体。

用户信息存储工具位于 `src/shared/utils/currentUser.ts`，页面通过 `src/shared/utils/useCurrentUser.ts` 响应式读取登录态。顶部用户区使用圆形头像入口，头像上传后会同步更新本地用户信息。

## Docker Notes

`apps/web/Dockerfile` 会先执行 `npm run build`，再把 `dist` 复制进 nginx 镜像。Docker Compose 部署时不是 Vite 热重载，修改前端源码后需要重建 `web` 服务：

```bash
docker compose -f deploy/docker-compose.yml up -d --build web
```
