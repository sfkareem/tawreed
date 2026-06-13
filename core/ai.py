import json
import re
import httpx
import openai
from datetime import datetime
from typing import List, Dict, Any, Tuple

PROVIDERS = {
    "OpenAI": {
        "base_url": "https://api.minimax.io/v1",
        "models": ["MiniMax-M3", "gpt-4o", "gpt-4o-mini", "o1"],
        "default_model": "MiniMax-M3",
        "requires_base_url": True,
        "transport": "openai",
        "label": "OpenAI (custom base URL)"
    },
    "Google": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "models": ["gemini-1.5-pro", "gemini-1.5-flash"],
        "default_model": "gemini-1.5-pro",
        "requires_base_url": False,
        "transport": "openai_compat",
        "label": "Google Gemini"
    },
    "Claude": {
        "base_url": "https://api.anthropic.com/v1",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
        "default_model": "claude-3-5-sonnet-20241022",
        "requires_base_url": False,
        "transport": "native_anthropic",
        "label": "Anthropic Claude"
    },
    "OpenAI Compatible": {
        "base_url": "",
        "models": [],
        "default_model": "",
        "requires_base_url": True,
        "transport": "openai",
        "label": "OpenAI-Compatible (custom)"
    }
}


def get_provider_names() -> list:
    """Return the list of supported provider keys, in display order."""
    return list(PROVIDERS.keys())


def get_provider_config(name: str) -> dict:
    """Return the full provider config for a given name.

    Raises KeyError if the name is not a recognised provider. Callers
    should validate user input via `is_valid_provider()` first.
    """
    return PROVIDERS[name]


def is_valid_provider(name: str) -> bool:
    """True if `name` is a key in the PROVIDERS dict."""
    return name in PROVIDERS


def get_default_settings() -> dict:
    """Return a complete default settings dict using the default provider."""
    default_provider = "OpenAI"
    p = PROVIDERS[default_provider]
    return {
        "provider": default_provider,
        "api_key": "",
        "model": p["default_model"],
        "base_url": p["base_url"],
    }

SYSTEM_PROMPT = """
You are an expert Quantity Surveyor and Construction Estimator.
Your task is to analyze Bill of Quantities (BOQ) items and categorize each item into a MACRO-LEVEL Work Package (e.g., Concrete Works, Masonry, HVAC, Plumbing, Electrical, Finishes).
DO NOT use granular item names as packages. Group related items into high-level trades.

You will receive a JSON dictionary of BOQ items, where the keys are row indices.
You must return a JSON dictionary where the keys are the corresponding row indices (e.g., "0", "1") and the values are the Work Package names.
Output ONLY valid JSON.
"""

class ContentStreamParser:
    def __init__(self):
        self.is_thought = False
        self.buffer = ""
        
    def feed(self, chunk: str):
        self.buffer += chunk
        yields = []
        
        while self.buffer:
            if not self.is_thought:
                idx = self.buffer.find("<think>")
                if idx != -1:
                    if idx > 0:
                        yields.append((self.buffer[:idx], False))
                    yields.append(("<think>", True))
                    self.is_thought = True
                    self.buffer = self.buffer[idx + 7:]
                else:
                    partial_len = 0
                    for i in range(1, min(7, len(self.buffer) + 1)):
                        suffix = self.buffer[-i:]
                        if "<think>".startswith(suffix):
                            partial_len = i
                    
                    if partial_len > 0:
                        send_len = len(self.buffer) - partial_len
                        if send_len > 0:
                            yields.append((self.buffer[:send_len], False))
                            self.buffer = self.buffer[send_len:]
                        break
                    else:
                        yields.append((self.buffer, False))
                        self.buffer = ""
            else:
                idx = self.buffer.find("</think>")
                if idx != -1:
                    if idx > 0:
                        yields.append((self.buffer[:idx], True))
                    yields.append(("</think>", False))
                    self.is_thought = False
                    self.buffer = self.buffer[idx + 8:]
                else:
                    partial_len = 0
                    for i in range(1, min(8, len(self.buffer) + 1)):
                        suffix = self.buffer[-i:]
                        if "</think>".startswith(suffix):
                            partial_len = i
                            
                    if partial_len > 0:
                        send_len = len(self.buffer) - self.block_len if (hasattr(self, 'block_len') and self.block_len) else len(self.buffer) - partial_len
                        if send_len > 0:
                            yields.append((self.buffer[:send_len], True))
                            self.buffer = self.buffer[send_len:]
                        break
                    else:
                        yields.append((self.buffer, True))
                        self.buffer = ""
        return yields

    def flush(self):
        if self.buffer:
            res = (self.buffer, self.is_thought)
            self.buffer = ""
            return [res]
        return []

def extract_json_from_text(text: str) -> dict:
    cleaned_text = text.strip()
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_match_fallback = re.search(r'(\{.*\})', cleaned_text, re.DOTALL)
        if json_match_fallback:
            json_str = json_match_fallback.group(1)
        else:
            json_str = cleaned_text
            
    try:
        parsed_data = json.loads(json_str)
    except Exception:
        try:
            fixed_json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
            parsed_data = json.loads(fixed_json_str)
        except Exception:
            parsed_data = {}
            
    if not isinstance(parsed_data, dict):
        return {}
        
    normalized_data = {}
    for k, v in parsed_data.items():
        k_str = str(k)
        if k_str == "items" and isinstance(v, dict):
            normalized_data["items"] = {str(item_k): str(item_v) for item_k, item_v in v.items()}
        else:
            normalized_data[k_str] = v
            
    return normalized_data

def analyze_boq_stream(api_key: str, base_url: str, model_id: str, system_prompt: str, user_prompt: str):
    try:
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=True,
            temperature=0.0
        )
        
        parser = ContentStreamParser()
        accumulated_content = []
        
        for chunk in response:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            
            reasoning = getattr(delta, "reasoning_content", None)
            if reasoning:
                yield (reasoning, True)
                continue
                
            content = getattr(delta, "content", None)
            if content:
                for token_text, is_thought in parser.feed(content):
                    yield (token_text, is_thought)
                    if not is_thought:
                        accumulated_content.append(token_text)
                        
        for token_text, is_thought in parser.flush():
            yield (token_text, is_thought)
            if not is_thought:
                accumulated_content.append(token_text)
                
        full_content_str = "".join(accumulated_content).strip()
        parsed_data = extract_json_from_text(full_content_str)
        if "project_name" not in parsed_data:
            parsed_data["project_name"] = "Tawreed Project"
        if "date" not in parsed_data:
            parsed_data["date"] = datetime.now().strftime("%Y-%m-%d")
        if "items" not in parsed_data:
            parsed_data["items"] = {}
        return parsed_data
        
    except Exception as e:
        print(f"Error in analyze_boq_stream: {e}")
        return {
            "project_name": "Tawreed Project",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "items": {},
            "error": str(e)
        }

async def test_connection(provider: str, api_key: str, model: str, base_url: str = "") -> bool:
    try:
        url = base_url if provider == "OpenAI Compatible" else PROVIDERS[provider]["base_url"]
        if not url:
            return False
            
        if provider == "Claude":
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            data = {
                "model": model,
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hello"}]
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{url.rstrip('/')}/messages", headers=headers, json=data, timeout=10.0)
                return resp.status_code == 200
        else:
            if provider == "OpenAI" and not url.endswith('/v1') and not url.endswith('/v1/'):
                url = f"{url.rstrip('/')}/v1"
                
            headers = {
                "Content-Type": "application/json"
            }
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
                
            data = {
                "model": model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            endpoint = f"{url.rstrip('/')}/chat/completions"
            async with httpx.AsyncClient() as client:
                resp = await client.post(endpoint, headers=headers, json=data, timeout=10.0)
                return resp.status_code == 200
    except Exception as e:
        print(f"test_connection exception: {e}")
        return False

async def process_boq_batch(items: list, provider: str, api_key: str, model: str, base_url: str = "") -> dict:
    try:
        items_json = json.dumps({str(i): item for i, item in enumerate(items)}, ensure_ascii=False)
        url = base_url if provider == "OpenAI Compatible" else PROVIDERS[provider]["base_url"]
        if not url:
            return {str(idx): "General" for idx in range(len(items))}
            
        result_text = ""
        if provider == "Claude":
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            data = {
                "model": model,
                "max_tokens": 4096,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": f"Categorize these items:\n{items_json}"}]
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{url.rstrip('/')}/messages", headers=headers, json=data, timeout=60.0)
                resp.raise_for_status()
                result_text = resp.json()["content"][0]["text"]
        else:
            if provider == "OpenAI" and not url.endswith('/v1') and not url.endswith('/v1/'):
                url = f"{url.rstrip('/')}/v1"
                
            headers = {
                "Content-Type": "application/json"
            }
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
                
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Categorize these items:\n{items_json}"}
                ],
                "temperature": 0.0,
                "response_format": {"type": "json_object"} if provider != "Claude" else None
            }
            endpoint = f"{url.rstrip('/')}/chat/completions"
            async with httpx.AsyncClient() as client:
                resp = await client.post(endpoint, headers=headers, json=data, timeout=60.0)
                resp.raise_for_status()
                result_text = resp.json()["choices"][0]["message"]["content"]
                
        parsed_data = extract_json_from_text(result_text)
        if parsed_data:
            if "items" in parsed_data and isinstance(parsed_data["items"], dict):
                items_dict = parsed_data["items"]
            else:
                items_dict = parsed_data
            return {str(k): str(v) for k, v in items_dict.items()}
        else:
            return {str(idx): "General" for idx in range(len(items))}
            
    except Exception as e:
        print(f"Error in process_boq_batch: {e}")
        return {str(idx): "General" for idx in range(len(items))}
