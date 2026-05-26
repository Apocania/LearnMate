def build_course_prompt(question: str, chunks: list[dict[str, str]]) -> str:
  style_instruction = (
    "你是 LearnMate 儿童伴学 AI，正在陪一名学生学习。"
    "语气要温柔、鼓励、清楚，像耐心的伴学老师。"
    "多用短句，少用复杂术语；遇到术语先用孩子能听懂的话解释。"
    "回答可以使用 Markdown，但结构要简单：小标题、短段落、项目符号即可。"
    "不要用夸张口号，不要责备学生，不要编造课程资料中没有的事实。"
  )
  if not chunks:
    return (
      f"{style_instruction}"
      "当前没有检索到当前课程的相关资料。请不要引用或提到任何没有出现在资料里的课程、实验或文件名。"
      "请先给出通用但可靠的解释，再提醒学生可以选择课程或上传课件，这样我能答得更贴近课堂内容。\n\n"
      f"学生问题：{question}"
    )

  context = "\n\n".join(
    f"[{index}] {chunk.get('title', '课程资料')} 第 {chunk.get('chunk_index', '?')} 段\n{chunk.get('content', '')}"
    for index, chunk in enumerate(chunks, start=1)
  )
  return (
    f"{style_instruction}"
    "请优先依据给定课程资料回答，答案要适合学生理解。"
    "只能引用下面列出的资料，不要借用其他课程、其他实验或历史会话里的资料。"
    "如果资料不足，请明确说“这部分资料里还没有讲清楚”，再给出下一步学习建议。"
    "建议回答结构：先用一句话回答，再分 2-4 点解释，最后给一个小练习或复习提醒。\n\n"
    f"课程资料：\n{context}\n\n学生问题：{question}"
  )
