import os
import re
import json
import time
import logging
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logger = logging.getLogger("AutoDevAI.GeminiService")

class GeminiService:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.fallback_models = [
            self.model_name,
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-pro"
        ]
        # Remove duplicates while preserving order
        seen = set()
        self.fallback_models = [m for m in self.fallback_models if m and not (m in seen or seen.add(m))]

        if self.api_key and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to configure Gemini with provided key: {e}")

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5 and GENAI_AVAILABLE)

    def set_api_key(self, api_key: str):
        self.api_key = api_key.strip()
        if self.api_key and GENAI_AVAILABLE:
            genai.configure(api_key=self.api_key)

    def clean_markdown_fences(self, text: str) -> str:
        """Removes markdown code fences like ```json or ```python from LLM outputs."""
        if not text:
            return ""
        # Match ```language \n ... \n ```
        cleaned = text.strip()
        cleaned = re.sub(r'^```[a-zA-Z0-9_-]*\s*\n', '', cleaned)
        cleaned = re.sub(r'\n```\s*$', '', cleaned)
        return cleaned.strip()

    def parse_json_safely(self, text: str) -> Dict[str, Any]:
        """Cleans and extracts valid JSON object/array from model output."""
        cleaned = self.clean_markdown_fences(text)
        
        # Try direct JSON parsing
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Try to find JSON block {...} or [...]
        match = re.search(r'(\{.*\}|\[.*\])', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        logger.warning("Failed to parse JSON directly. Returning fallback structured dict.")
        return {"raw_content": text}

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        json_mode: bool = False,
        max_retries: int = 3,
        temperature: float = 0.2
    ) -> str:
        """Executes LLM text generation with exponential backoff and model fallbacks."""
        if not self.is_configured():
            logger.info("Gemini API key not configured or genai unavailable. Using fallback offline heuristics.")
            raise ValueError("GEMINI_API_KEY is not configured.")

        last_error = None
        for model_to_try in self.fallback_models:
            for attempt in range(1, max_retries + 1):
                try:
                    generation_config = {
                        "temperature": temperature,
                        "top_p": 0.95,
                    }
                    if json_mode:
                        generation_config["response_mime_type"] = "application/json"

                    model = genai.GenerativeModel(
                        model_name=model_to_try,
                        system_instruction=system_instruction,
                        generation_config=generation_config
                    )

                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text.strip()
                    else:
                        raise ValueError("Empty response received from Gemini API.")

                except Exception as e:
                    last_error = e
                    err_str = str(e).lower()
                    logger.warning(f"Gemini generation attempt {attempt} on model {model_to_try} failed: {e}")

                    # Check for rate limit or retryable errors
                    is_rate_limit = any(term in err_str for term in ["429", "quota", "resource_exhausted", "503", "unavailable", "timeout"])
                    if is_rate_limit and attempt < max_retries:
                        sleep_time = (2 ** attempt) + 0.5
                        logger.info(f"Rate limit / transient error encountered. Backing off for {sleep_time:.1f}s...")
                        time.sleep(sleep_time)
                    else:
                        # Non-retryable or max retries reached for this model; try next fallback model
                        break

        raise RuntimeError(f"Gemini generation failed across all models. Last error: {last_error}")

    def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_retries: int = 3,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Generates structured JSON with parsing guarantees."""
        text = self.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            json_mode=True,
            max_retries=max_retries,
            temperature=temperature
        )
        return self.parse_json_safely(text)

gemini_service = GeminiService()
