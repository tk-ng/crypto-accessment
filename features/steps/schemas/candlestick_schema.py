schema = {
    "type": "object",
    "properties": {
            "id": {"type": "integer"},
        "method": {"type": "string"},
        "code": {"type": "integer"},
        "result": {
                "type": "object",
                "properties": {
                        "interval": {"type": "string"},
                        "instrument_name": {"type": "string"},
                        "data": {
                            "type": "array",
                            "items": {
                                    "type": "object",
                                "properties": {
                                            "o": {"type": "string"},
                                            "h": {"type": "string"},
                                            "l": {"type": "string"},
                                            "c": {"type": "string"},
                                            "v": {"type": "string"},
                                            "t": {"type": "integer"}
                                },
                                "required": ["o", "h", "l", "c", "v", "t"],
                                "additionalProperties": False
                            }
                        }
                },
                "required": ["interval", "data", "instrument_name"],
                "additionalProperties": False
        }
    },
    "required": ["id", "method", "code", "result"],
    "additionalProperties": False
}
