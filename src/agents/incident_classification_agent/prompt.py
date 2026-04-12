
SYSTEM_PROMPT = (
	"You are an incident classification assistant for mining operations. "
	"Use the efficientnet0_classify tool to verify image context when images are provided. "
	"Return JSON only with fields: description, status, location, severity, incidentType."
)


def build_user_prompt(
	description: str,
	image_b64: list,
	image_labels: list,
	config: dict,
) -> str:
	incident_types = config.get("incidentTypes", [])
	return (
		"Classify the incident into JSON with fields: "
		"description, status, location, severity, incidentType. "
		"Use severity values from config.json for the chosen incident type. "
		"If uncertain, choose the closest incidentType from config.json. "
		"Return JSON only.\n\n"
		"Examples of mining incidents include: "
		"roof fall, gas exposure, equipment collision, conveyor fire, "
		"explosives mishandling, haul truck incident, rock burst.\n\n"
		f"Config incident types: {incident_types}\n\n"
		f"Incident description: {description}\n\n"
		f"Image labels (EfficientNet): {image_labels}\n\n"
		f"Images (base64, optional): {image_b64}"
	)
