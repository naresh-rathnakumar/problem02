"""
Ollama client wrapper for local LLM inference via LangChain.
Enforces local Ollama only. No cloud LLM fallback.
Provides transparent connection checking, JSON extraction, and structured diagnostics.
"""

import os
import json
import re
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class OllamaClient:
    """Client for local Ollama LLM integration via LangChain ChatOllama."""

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
        self._llm = None

    @property
    def llm(self):
        """Lazy initialization of ChatOllama."""
        if self._llm is None:
            try:
                from langchain_ollama import ChatOllama
                self._llm = ChatOllama(
                    model=self.model,
                    base_url=self.base_url,
                    temperature=0.1,
                    timeout=self.timeout,
                )
            except Exception as e:
                # Fallback to langchain_community.chat_models if langchain_ollama differs
                try:
                    from langchain_community.chat_models import ChatOllama
                    self._llm = ChatOllama(
                        model=self.model,
                        base_url=self.base_url,
                        temperature=0.1,
                        timeout=self.timeout,
                    )
                except Exception:
                    raise RuntimeError(f"Could not initialize ChatOllama: {e}")
        return self._llm

    def check_connection(self) -> Dict[str, Any]:
        """Check if local Ollama daemon is reachable and if the configured model is pulled."""
        result = {
            "connected": False,
            "model_available": False,
            "model_name": self.model,
            "base_url": self.base_url,
            "available_models": [],
            "error": None
        }

        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if response.status_code == 200:
                result["connected"] = True
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                result["available_models"] = models

                model_base = self.model.split(":")[0]
                for m in models:
                    if m.split(":")[0] == model_base or m == self.model or self.model in m:
                        result["model_available"] = True
                        break
            else:
                result["error"] = f"Ollama HTTP {response.status_code}"
        except requests.ConnectionError:
            result["error"] = "Cannot connect to local Ollama service. Daemon may be stopped."
        except requests.Timeout:
            result["error"] = "Connection to local Ollama timed out."
        except Exception as e:
            result["error"] = f"Connection error: {str(e)}"

        return result

    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        """Invoke local Ollama using LangChain messages."""
        from langchain_core.messages import SystemMessage, HumanMessage
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self.llm.invoke(messages)
        return response.content

    def invoke_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Invoke local Ollama and parse strictly structured JSON."""
        content = self.invoke(system_prompt, user_prompt)
        return self._extract_json(content)

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract and parse JSON from LLM output, with multi-strategy regex recovery."""
        if not text:
            return {"parse_error": "Empty response"}

        # 1. Direct parse
        try:
            return json.loads(text.strip())
        except Exception:
            pass

        # 2. Markdown fenced blocks ```json ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            try:
                return json.loads(fence_match.group(1).strip())
            except Exception:
                pass

        # 3. Outer braces { ... }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                pass

        return {"raw_text": text, "parse_error": "Failed to decode JSON from model output"}

    @staticmethod
    def get_setup_instructions() -> str:
        model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        return f"""### Local Ollama Setup & Configuration

This system runs **strictly on local Ollama LLMs**. Cloud APIs are prohibited.

1. **Install Ollama**
   - Download for Windows from: `https://ollama.com/download/windows`
2. **Start the Ollama daemon**
   - Open PowerShell or Terminal and execute:
     ```powershell
     ollama serve
     ```
3. **Pull the configured model**
   - Execute:
     ```powershell
     ollama pull {model}
     ```
4. **Verify running model**
   - Execute:
     ```powershell
     ollama list
     ```
5. **Change Model via .env**
   - Edit `.env` to configure any locally available model (e.g. `mistral`, `gemma2:9b`, `qwen2.5:7b`).
"""
