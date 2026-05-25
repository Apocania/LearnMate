# Knowledge Base

更新日期：2026-05-23

这里可以存放 AI 助教演示用的课程资料样例。

当前后端会在课件上传后自动抽取文本、切分 chunk，并写入数据库 `knowledge_chunks` 供 AI 伴学检索。课件文件可使用本地存储或 MinIO：

```text
STORAGE_BACKEND=local
STORAGE_BACKEND=minio
```

生产环境中，建议通过上传接口写入真实课件，让数据库保存对应元数据和知识库切片；本目录更适合作为离线样例、说明文档或人工准备素材的位置。
