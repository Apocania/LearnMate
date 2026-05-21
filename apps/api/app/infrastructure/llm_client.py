import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings


class LLMClient:
  def chat(self, prompt: str) -> str:
    if settings.llm_api_key and settings.llm_base_url and settings.llm_model:
      return self._chat_openai_compatible(prompt)
    return self._chat_local(prompt)

  def _chat_openai_compatible(self, prompt: str) -> str:
    url = settings.llm_base_url.rstrip("/")
    if not url.endswith("/chat/completions"):
      url = f"{url}/chat/completions"
    payload = {
      "model": settings.llm_model,
      "messages": [
        {"role": "system", "content": "你是 LearnMate 的课程伴学助手。"},
        {"role": "user", "content": prompt},
      ],
      "temperature": 0.2,
    }
    request = Request(
      url,
      data=json.dumps(payload).encode("utf-8"),
      headers={
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
      },
      method="POST",
    )
    try:
      with urlopen(request, timeout=30) as response:
        body = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
      raise RuntimeError("大模型服务暂时不可用") from exc

    try:
      return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
      raise RuntimeError("大模型响应格式异常") from exc

  def _chat_local(self, prompt: str) -> str:
    if "课程资料：" not in prompt:
      return (
        "我还没有检索到可引用的课程资料，因此只能给出通用学习建议：请先明确问题中的核心概念、"
        "列出已知条件，再对照课件或教材逐步验证。上传课件或选择课程后，我可以结合资料回答得更具体。"
      )

    question = prompt.split("学生问题：", 1)[-1].strip()
    context = prompt.split("课程资料：", 1)[-1].split("学生问题：", 1)[0].strip()
    excerpts = [line.strip() for line in context.splitlines() if line.strip() and not line.startswith("[")]
    selected = "；".join(excerpts[:3]) or "当前资料片段较短，建议结合课程原文继续核对。"
    return (
      f"根据已检索到的课程资料，关于“{question}”可以这样理解：{selected}。"
      "你可以先抓住这些关键词复述一遍，再回到课程资料中查看对应段落；如果还不清楚，继续追问具体概念或例题。"
    )
