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
- `/forum`：讨论交流。游客可浏览；登录用户可发帖、评论、点赞；伴学师可删除帖子。
- `/files`：文件资料。游客和学生可浏览/下载；伴学师可上传课件，并删除自己上传的课件。
- `/assistant`：AI 伴学。登录后可向后端发送问题，游客会看到登录提示。
- `/reports/me`：个人中心/学习报告，目前仍以静态展示为主。

## API Client Behavior

`src/api/client.ts` 会统一处理请求：

- 从 `VITE_API_BASE_URL` 读取后端 API 地址。
- 自动附加 `learnmate_access_token`。
- 上传 `FormData` 时不强制设置 JSON header。
- 遇到 `401` 会清除本地登录信息并跳转 `/login`。
- 支持 `204 No Content` 和空响应体。

用户信息存储工具位于 `src/shared/utils/currentUser.ts`。
