schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "method", "code", "result"],
    "properties": {
        "id": {"type": "integer"},
        "method": {"type": "string"},
        "code": {"type": "integer", "enum": [0]},
        "result": {
            "type": "object",
            "required": ["instrument_name", "subscription", "channel", "depth", "data"],
            "properties": {
                "instrument_name": {"type": "string"},
                "subscription": {"type": "string"},
                "channel": {"type": "string", "enum": ["book"]},
                "depth": {"type": ["integer", "string"]},
                "data": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["bids", "asks", "tt", "t", "u"],
                        "properties": {
                            "bids": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "minItems": 3,
                                    "maxItems": 3,
                                    "items": {"type": "string"}
                                }
                            },
                            "asks": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "minItems": 3,
                                    "maxItems": 3,
                                    "items": {"type": "string"}
                                }
                            },
                            "tt": {"type": "integer"},
                            "t": {"type": "integer"},
                            "u": {"type": "integer"}
                        }
                    }
                }
            }
        }
    }
}
