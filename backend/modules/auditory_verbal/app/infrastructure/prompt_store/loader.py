import os
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger


class PromptLoader:
    """Prompt management repository skeleton for version-controlled LLM prompt templates."""

    def __init__(self, prompt_dir: str = os.path.join(settings.CONFIG_REPO_PATH, "prompts")):
        self.prompt_dir = prompt_dir
        self._prompts: Dict[str, str] = {}

    def get_prompt_template(self, prompt_key: str) -> str:
        file_path = os.path.join(self.prompt_dir, f"{prompt_key}.yaml")
        if not os.path.exists(file_path):
            logger.warning(f"Prompt template '{prompt_key}' not found at '{file_path}'. Using generic fallback.")
            return "Extract evidence for construct evaluation."
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            self._prompts[prompt_key] = content
            return content


# Singleton prompt loader instance
prompt_loader = PromptLoader()
