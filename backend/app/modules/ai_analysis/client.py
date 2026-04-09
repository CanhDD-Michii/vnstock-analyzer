from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.modules.ai_analysis.parser import parse_ai_json_response
from app.modules.ai_analysis.prompt_builder import openai_output_schema_hint


def call_openai_analysis(
    system_prompt: str,
    user_message: str,
) -> dict[str, Any]:
    if not settings.openai_enabled:
        raise RuntimeError("OpenAI chưa được cấu hình (OPENAI_API_KEY)")
    client = OpenAI(api_key=settings.openai_api_key)
    schema_hint = openai_output_schema_hint()
    full_user = user_message + "\n\nSCHEMA_JSON:\n" + schema_hint
    resp = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.35,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user},
        ],
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content or ""
    return parse_ai_json_response(content)
