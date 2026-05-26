import json
import time
from socket import timeout as SocketTimeout
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings

RETRYABLE_HTTP_STATUS = {408, 429, 500, 502, 503, 504}
RETRY_DELAYS_SECONDS = (0.5, 1.2)


class LLMClient:
  def chat(self, prompt: str) -> str:
    if settings.llm_api_key and settings.llm_base_url and settings.llm_model:
      try:
        return self._chat_openai_compatible(prompt)
      except RuntimeError as exc:
        return self._build_fallback_answer(prompt, exc)
    return self._chat_local(prompt)

  def stream_chat(self, prompt: str):
    if settings.llm_api_key and settings.llm_base_url and settings.llm_model:
      try:
        yield from self._stream_openai_compatible(prompt)
      except RuntimeError as exc:
        yield from self._chunk_text(self._build_fallback_answer(prompt, exc))
      return

    answer = self._chat_local(prompt)
    for chunk in self._chunk_text(answer):
      yield chunk
      time.sleep(0.015)

  def _chat_openai_compatible(self, prompt: str) -> str:
    payload = self._build_payload(prompt)
    body = self._request_json_with_retry(payload)

    try:
      return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
      raise RuntimeError("大模型响应格式异常") from exc

  def _stream_openai_compatible(self, prompt: str):
    payload = self._build_payload(prompt, stream=True)
    yield from self._stream_with_retry(payload)

  def _request_json_with_retry(self, payload: dict) -> dict:
    last_error: RuntimeError | None = None
    for attempt in range(len(RETRY_DELAYS_SECONDS) + 1):
      request = self._build_request(payload)
      try:
        with urlopen(request, timeout=30) as response:
          return json.loads(response.read().decode("utf-8"))
      except HTTPError as exc:
        error = RuntimeError(self._format_http_error(exc))
        if exc.code not in RETRYABLE_HTTP_STATUS or attempt >= len(RETRY_DELAYS_SECONDS):
          raise error from exc
        last_error = error
      except (URLError, TimeoutError, SocketTimeout) as exc:
        error = RuntimeError(f"大模型服务暂时不可用：网络连接失败或超时（{exc.reason if isinstance(exc, URLError) else exc}）")
        if attempt >= len(RETRY_DELAYS_SECONDS):
          raise error from exc
        last_error = error
      except json.JSONDecodeError as exc:
        raise RuntimeError("大模型响应不是有效 JSON，请检查 LLM_BASE_URL 是否填到了 OpenAI 兼容接口") from exc
      time.sleep(RETRY_DELAYS_SECONDS[attempt])
    raise last_error or RuntimeError("大模型服务暂时不可用")

  def _stream_with_retry(self, payload: dict):
    last_error: RuntimeError | None = None
    for attempt in range(len(RETRY_DELAYS_SECONDS) + 1):
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
              if "error" in event:
                raise RuntimeError(self._format_provider_error(event["error"]))
              choices = event.get("choices") or []
              if not choices:
                continue
              content = choices[0].get("delta", {}).get("content", "") or ""
            except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
              raise RuntimeError("大模型流式响应格式异常") from exc
            if content:
              yield content
          return
      except HTTPError as exc:
        error = RuntimeError(self._format_http_error(exc))
        if exc.code not in RETRYABLE_HTTP_STATUS or attempt >= len(RETRY_DELAYS_SECONDS):
          raise error from exc
        last_error = error
      except (URLError, TimeoutError, SocketTimeout) as exc:
        error = RuntimeError(f"大模型服务暂时不可用：网络连接失败或超时（{exc.reason if isinstance(exc, URLError) else exc}）")
        if attempt >= len(RETRY_DELAYS_SECONDS):
          raise error from exc
        last_error = error
      time.sleep(RETRY_DELAYS_SECONDS[attempt])
    raise last_error or RuntimeError("大模型服务暂时不可用")

  def _build_payload(self, prompt: str, stream: bool = False) -> dict:
    payload = {
      "model": settings.llm_model,
      "messages": [
        {
          "role": "system",
          "content": (
            "你是 LearnMate 的儿童伴学 AI。请用温柔、鼓励、清楚的中文回答，"
            "像耐心的伴学老师一样陪学生一步步理解。"
          ),
        },
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

  def _format_http_error(self, exc: HTTPError) -> str:
    detail = ""
    try:
      raw_body = exc.read().decode("utf-8")
      body = json.loads(raw_body)
      detail = self._format_provider_error(body.get("error") or body)
    except (json.JSONDecodeError, UnicodeDecodeError):
      detail = "服务返回了非 JSON 错误"
    except Exception:
      detail = "无法读取服务错误详情"

    hints = {
      400: "请求格式或模型参数不被该平台支持，请检查 LLM_MODEL 和 Base URL。",
      401: "API Key 无效或没有权限，请检查 LLM_API_KEY。",
      403: "账号无权访问该模型或接口，请检查模型权限。",
      404: "接口地址或模型不存在，请检查 LLM_BASE_URL 和 LLM_MODEL。",
      429: "请求过快、额度不足或触发限流，请稍后重试或检查余额。",
    }
    hint = hints.get(exc.code, "请查看模型平台控制台日志。")
    return f"大模型调用失败：HTTP {exc.code}。{hint} 服务返回：{detail}"

  def _format_provider_error(self, error: object) -> str:
    if isinstance(error, dict):
      message = error.get("message") or error.get("msg") or error.get("detail") or str(error)
      code = error.get("code") or error.get("type")
      return f"{message}{f'（{code}）' if code else ''}"
    return str(error)

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

  def _build_fallback_answer(self, prompt: str, error: RuntimeError) -> str:
    local_answer = self._chat_local(prompt)
    return (
      "模型服务刚刚有点忙，我先根据已经检索到的课程资料陪你继续学。\n\n"
      f"{local_answer}\n\n"
      f"> 小提示：如果你连续看到这句话，可能是模型平台临时繁忙。错误信息：{error}"
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
