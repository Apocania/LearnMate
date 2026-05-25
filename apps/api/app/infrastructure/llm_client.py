import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings


class LLMClient:
  def chat(self, prompt: str) -> str:
    if settings.llm_api_key and settings.llm_base_url and settings.llm_model:
      return self._chat_openai_compatible(prompt)
    return self._chat_local(prompt)

  def stream_chat(self, prompt: str):
    if settings.llm_api_key and settings.llm_base_url and settings.llm_model:
      yield from self._stream_openai_compatible(prompt)
      return

    answer = self._chat_local(prompt)
    for chunk in self._chunk_text(answer):
      yield chunk
      time.sleep(0.015)

  def _chat_openai_compatible(self, prompt: str) -> str:
    payload = self._build_payload(prompt)
    request = self._build_request(payload)
    try:
      with urlopen(request, timeout=30) as response:
        body = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
      raise RuntimeError("大模型服务暂时不可用") from exc

    try:
      return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
      raise RuntimeError("大模型响应格式异常") from exc

  def _stream_openai_compatible(self, prompt: str):
    payload = self._build_payload(prompt, stream=True)
    request = self._build_request(payload)
    try:
      with urlopen(request, timeout=60) as response:
        for raw_line in response:
          line = raw_line.decode("utf-8").strip()
          if not line or not line.startswith("data:"):
            continue
          data = line.removeprefix("data:").strip()
          if data == "[DONE]":
            break
          try:
            event = json.loads(data)
            content = event["choices"][0].get("delta", {}).get("content", "")
          except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("大模型流式响应格式异常") from exc
          if content:
            yield content
    except (HTTPError, URLError, TimeoutError) as exc:
      raise RuntimeError("大模型服务暂时不可用") from exc

  def _build_payload(self, prompt: str, stream: bool = False) -> dict:
    payload = {
      "model": settings.llm_model,
      "messages": [
        {"role": "system", "content": "你是 LearnMate 的课程伴学助手。"},
        {"role": "user", "content": prompt},
      ],
      "temperature": 0.2,
    }
    if stream:
      payload["stream"] = True
    return payload

  def _build_request(self, payload: dict) -> Request:
    url = settings.llm_base_url.rstrip("/")
    if not url.endswith("/chat/completions"):
      url = f"{url}/chat/completions"
    return Request(
      url,
      data=json.dumps(payload).encode("utf-8"),
      headers={
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
      },
      method="POST",
    )

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

  def _chunk_text(self, text: str, size: int = 12):
    buffer = ""
    for char in text:
      buffer += char
      if len(buffer) >= size or char in "。！？；\n":
        yield buffer
        buffer = ""
    if buffer:
      yield buffer
