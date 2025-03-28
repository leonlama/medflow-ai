import jsonschema
from datetime import datetime
import json


MEDICAL_SCHEMA = {
    "type": "object",
    "required": ["patient_id", "date", "treatment"],
    "properties": {
        "patient_id": {"type": "string", "pattern": "^[A-Z0-9-]+$"},
        "date": {"type": "string", "format": "date"},
        "treatment": {
            "type": "object",
            "required": ["medications"],
            "properties": {
                "medications": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "dose"],
                        "properties": {
                            "name": {"type": "string"},
                            "dose": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
}


def validate_medical_data(data: dict) -> tuple:
    try:
        jsonschema.validate(data, MEDICAL_SCHEMA)
        return True, None
    except jsonschema.ValidationError as e:
        return False, f"Validation failed: {e.message} at {'.'.join(str(p) for p in e.path)}"
    except Exception as e:
        return False, f"Unexpected validation error: {str(e)}"


class MedicalJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def remove_empty_elements(d):
    if not isinstance(d, dict):
        return d
    return {
        k: remove_empty_elements(v)
        for k, v in d.items()
        if v not in [None, "", [], {}]
    }
