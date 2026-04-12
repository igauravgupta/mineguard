from __future__ import annotations

from typing import List

from langchain.tools import tool

from config.logger import get_logger


logger = get_logger(__name__)


@tool("efficientnet0_classify")
def efficientnet0_classify(images_b64: List[str]) -> List[str]:
    """Classify incident images with EfficientNet-B0 (dummy implementation)."""
    if not images_b64:
        return []
    logger.info("EfficientNet0 tool invoked with %d image(s)", len(images_b64))
    return ["mining_site", "equipment", "personnel"]
