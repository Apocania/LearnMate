# LearnMate Web

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

## Main Pages

- `/login`：登录和注册，注册时可选择学生或伴学师，包含确认密码和用户名规则提示。
- `/courses`：课程中心。游客可浏览；学生可加入/退出课程；伴学师可创建、编辑、删除自己创建的课程，并进入课件管理。
- `/courses/:courseId`：课程详情。展示真实课程信息、选课人数和本人加入状态，学生可加入/退出。
- `/forum`：讨论交流。游客可浏览；登录用户可展开评论区直接评论和点赞，并删除自己的评论；伴学师可删除帖子和评论。列表中的长帖子会自动折叠，展开全文、点赞和评论统一在帖子右下角横向排列。
- `/forum/new`：独立发帖页。支持标题、Markdown 正文编辑/实时预览和最多 5 个附件上传。
- `/files`：文件资料。游客和学生可浏览/下载；伴学师可上传课件，并删除自己上传的课件。
- `/assistant`：AI 伴学。登录后可向后端发送问题，游客会看到登录提示。
- `/messages`：消息中心。学生可查看点赞、评论、私信、公告提醒；伴学师可发送私信和公告。
- `/reports/me`：个人中心/学习报告。登录后读取后端统计，展示课程、讨论、进度和建议。

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
