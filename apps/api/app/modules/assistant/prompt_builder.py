def build_course_prompt(question: str, chunks: list[dict[str, str]]) -> str:
  context = "\n\n".join(chunk.get("content", "") for chunk in chunks)
  return f"请基于课程资料回答学生问题。\n\n课程资料：\n{context}\n\n学生问题：{question}"

