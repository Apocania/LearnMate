# AI Assistant Design

本文档用于记录 AI 助教模块设计。

第一版建议采用 RAG：

```text
用户问题 -> 向量检索课程资料 -> 构造 Prompt -> 调用大模型 -> 返回带引用的回答
```

