# Smart Assistant Design

更新日期：2026-05-25

本文档用于记录智能伴学模块设计。

智能伴学第一版目标是轻量 RAG 闭环：

```text
上传课件 -> 抽取文本 -> 切分 chunk -> 用户问题 -> 检索课程资料 -> 构造 Prompt -> 调用大模型或本地回答 -> 返回带引用的回答
```

## Current Status

当前已经完成：

- 前端 `/assistant` 页面可以输入问题并调用后端。
- 游客会看到登录提示，不能直接使用智能伴学。
- 后端 `POST /api/assistant/messages` 需要登录用户，并允许 `student` / `mentor` 使用。
- 请求结构支持 `content`、可选 `course_id` 和可选 `session_id`。
- 响应结构包含 `session_id`、`answer` 和 `citations`。
- 后端已经拆出 `AssistantChatService`、`RetrievalService`、`prompt_builder`、`VectorStore`、`LLMClient` 等边界。
- 课件上传后会解析文本、切分 chunk 并写入 `knowledge_chunks`。
- `VectorStore.search()` 已实现本地 embedding 余弦相似度 + 关键词的混合资料检索。
- `LLMClient.chat()` 支持 OpenAI 兼容大模型配置；未配置时使用本地检索式回答。
- 智能伴学问答会写入 `assistant_sessions`、`assistant_messages` 和 `learning_events`。
- 学生学习报告和伴学师教学看板会统计智能伴学相关行为，用于展示学习轨迹或教学动态。

当前仍可继续增强：

- 本地 embedding 检索可升级为 pgvector 原生索引和外部 embedding 模型。
- PDF 解析依赖 `pypdf`；图片 OCR 尚未接入。
- 输入限流、回答长度控制、内容安全边界、流式输出、用户反馈和多轮上下文精细控制仍可继续完善。

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

1. 增加输入 schema 限制、单用户频率限制、模型 `max_tokens` 上限、拒答边界和输出安全检查。
2. 将本地哈希 embedding 升级为外部 embedding 模型，并使用 pgvector 原生向量列和索引。
3. 增加 SSE 流式输出，让长回答在前端逐步呈现。
4. 增加会话列表、历史消息查询接口和多轮上下文 token 预算控制。
5. 增加回答点赞/点踩反馈、人工复核标记和评测样例集。
6. 增加图片/PDF 扫描件 OCR，把更多课件内容纳入知识库。
