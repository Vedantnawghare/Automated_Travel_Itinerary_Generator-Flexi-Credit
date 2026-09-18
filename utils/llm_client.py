import os
import json
import re
from typing import Dict, Any, List, Optional


DEFAULT_MODEL = "openai/gpt-oss-120b"


def get_groq_api_key() -> Optional[str]:
    """Retrieve Groq API key from environment or Streamlit secrets."""
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key.strip()
    try:
        import streamlit as st
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"].strip()
    except Exception:
        pass
    return None


def get_groq_model() -> str:
    """Retrieve Groq model from environment or Streamlit secrets, default to openai/gpt-oss-120b."""
    model = os.getenv("GROQ_MODEL")
    if model:
        return model.strip()
    try:
        import streamlit as st
        if "GROQ_MODEL" in st.secrets:
            return st.secrets["GROQ_MODEL"].strip()
    except Exception:
        pass
    return DEFAULT_MODEL


def is_groq_configured() -> bool:
    key = get_groq_api_key()
    return bool(key and key != "your_groq_api_key_here")


def clean_json_response(raw_text: str) -> Dict[str, Any]:
    """Extract and parse JSON from an LLM response even if wrapped in markdown codeblocks."""
    text = raw_text.strip()
    # Match markdown json fences
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    else:
        # Match from first '{' to last '}'
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]
    
    return json.loads(text)


def call_groq(
    messages: List[Dict[str, str]],
    json_mode: bool = True,
    temperature: float = 0.2,
    model: Optional[str] = None
) -> str:
    """
    Call Groq API with proper configuration, model selection, and error handling.
    """
    api_key = get_groq_api_key()
    if not is_groq_configured():
        raise ValueError("GROQ_API_KEY is not configured in environment or Streamlit secrets.")

    from groq import Groq
    target_model = model or get_groq_model()
    client = Groq(api_key=api_key)

    kwargs: Dict[str, Any] = {
        "model": target_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 4096,
    }

    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    chat_completion = client.chat.completions.create(**kwargs)
    content = chat_completion.choices[0].message.content
    return content or "{}"
