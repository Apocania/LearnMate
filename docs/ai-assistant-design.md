# AI Assistant Design

本文档用于记录 AI 助教模块设计。

AI 伴学第一版目标仍是 RAG：

```text
用户问题 -> 向量检索课程资料 -> 构造 Prompt -> 调用大模型 -> 返回带引用的回答
```

## Current Status

当前已经完成：

- 前端 `/assistant` 页面可以输入问题并调用后端。
- 游客会看到登录提示，不能直接使用 AI 伴学。
- 后端 `POST /api/assistant/messages` 需要登录用户，并允许 `student` / `mentor` 使用。
- 请求结构支持 `content` 和可选 `course_id`。
- 响应结构包含 `answer` 和 `citations`。
- 后端已经拆出 `AssistantChatService`、`RetrievalService`、`prompt_builder`、`VectorStore`、`LLMClient` 等边界。

当前仍是占位：

- `VectorStore.search()` 暂未真正检索课程资料。
- `LLMClient.chat()` 暂未调用真实大模型。
- `citations` 当前返回空列表。
- 对话记录、流式输出和用户反馈尚未落库。

## Runtime Flow

```text
AssistantPage.tsx
  -> apps/web/src/api/assistant.ts
  -> POST /api/assistant/messages
  -> assistant/api.py 鉴权
  -> AssistantChatService.answer()
  -> RetrievalService.retrieve()
  -> VectorStore.search()
  -> build_prompt()
  -> LLMClient.chat()
  -> AssistantMessageResponse
```

## Next Steps

1. 上传课件后解析文本。
2. 将文本切分为 chunk。
3. 生成 embedding。
4. 存入 pgvector。
5. 提问时按 `course_id` 检索相关资料。
6. 调用真实大模型。
7. 返回回答和引用来源。
8. 保存会话和消息记录。
