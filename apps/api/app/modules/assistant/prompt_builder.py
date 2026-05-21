def build_course_prompt(question: str, chunks: list[dict[str, str]]) -> str:
  if not chunks:
    return (
      "你是 LearnMate AI 伴学。当前没有检索到课程资料，请用清晰、谨慎的方式回答，"
      "并提醒用户可以上传或选择课程资料来获得更贴近课程的答案。\n\n"
      f"学生问题：{question}"
    )

  context = "\n\n".join(
    f"[{index}] {chunk.get('title', '课程资料')} 第 {chunk.get('chunk_index', '?')} 段\n{chunk.get('content', '')}"
    for index, chunk in enumerate(chunks, start=1)
  )
  return (
    "你是 LearnMate AI 伴学。请优先依据给定课程资料回答，答案要适合学生理解。"
    "如果资料不足，请明确说明不确定之处，并给出下一步学习建议。\n\n"
    f"课程资料：\n{context}\n\n学生问题：{question}"
  )
