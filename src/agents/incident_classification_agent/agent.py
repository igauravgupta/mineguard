from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain.agents import create_agent

from config.logger import get_logger
from providers.llm import LLMProvider
from agents.incident_classification_agent.prompt import SYSTEM_PROMPT, build_user_prompt
from agents.incident_classification_agent.tools import efficientnet0_classify


logger = get_logger(__name__)


def _read_image_bytes(image_file: Any) -> Optional[bytes]:
	if image_file is None:
		return None
	if hasattr(image_file, "getvalue"):
		return image_file.getvalue()
	if hasattr(image_file, "read"):
		return image_file.read()
	if isinstance(image_file, (bytes, bytearray)):
		return bytes(image_file)
	return None


def _encode_images_base64(images: List[Any]) -> List[str]:
	encoded = []
	for image in images or []:
		data = _read_image_bytes(image)
		if not data:
			continue
		encoded.append(base64.b64encode(data).decode("ascii"))
	return encoded


def _strip_json_fences(text: str) -> str:
	cleaned = text.strip()
	if cleaned.startswith("```"):
		cleaned = cleaned.strip("`")
		if cleaned.lower().startswith("json"):
			cleaned = cleaned[4:].strip()
	return cleaned


def _load_config() -> Dict[str, Any]:
	config_path = Path(__file__).with_name("config.json")
	try:
		return json.loads(config_path.read_text(encoding="utf-8"))
	except Exception as exc:
		logger.error("Failed to load config.json: %s", exc)
		return {"incidentTypes": []}


def _lookup_incident_config(config: Dict[str, Any], incident_type: str) -> Dict[str, Any]:
	incident_types = config.get("incidentTypes", [])
	for item in incident_types:
		if item.get("name", "").lower() == incident_type.lower():
			return item
	return {}


class ClassifyIncidentAgent:
	"""Classify incidents using LLM reasoning and image hints."""

	def __init__(self) -> None:
		self.logger = get_logger(__name__)
		self.llm = LLMProvider()
		self.config = _load_config()
		self.agent = create_agent(
			model=self.llm.get_chat_model(),
			tools=[efficientnet0_classify],
			system_prompt=SYSTEM_PROMPT,
		)

	def classify(
		self,
		description: str,
		images: Optional[List[Any]] = None,
	) -> Optional[Dict[str, Any]]:
		if not description:
			self.logger.error("Missing incident description")
			return None

		image_b64 = _encode_images_base64(images or [])
		try:
			image_labels = efficientnet0_classify.invoke({"images_b64": image_b64})
		except Exception as exc:
			self.logger.warning("EfficientNet tool failed: %s", exc)
			image_labels = []

		prompt = build_user_prompt(
			description=description,
			image_b64=image_b64,
			image_labels=image_labels,
			config=self.config,
		)

		try:
			result = self.agent.invoke(
				{"messages": [{"role": "user", "content": prompt}]}
			)
			output = result.get("output", "")
			if not output and isinstance(result.get("messages"), list):
				last_message = result["messages"][-1]
				output = getattr(last_message, "content", "") or last_message.get(
					"content", ""
				)
			cleaned = _strip_json_fences(output)
			payload = json.loads(cleaned)

			incident_type = str(payload.get("incidentType", "")).strip()
			config_entry = _lookup_incident_config(self.config, incident_type)
			if config_entry:
				payload.setdefault("severity", config_entry.get("severity"))
				payload["notifyEmails"] = config_entry.get("notify", [])

			return payload
		except Exception as exc:
			self.logger.error("Incident classification failed: %s", exc)
			return None
