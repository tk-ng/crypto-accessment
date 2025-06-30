schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Orderbook Delta Update Schema",
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "method": {"type": "string"},
        "code": {"type": "integer", "const": 0},
        "result": {
            "type": "object",
            "properties": {
                "instrument_name": {"type": "string"},
                "subscription": {"type": "string"},
                "channel": {"type": "string", "const": "book.update"},
                "depth": {
                    "oneOf": [
                        {"type": "integer"},
                        {"type": "string"}
                    ]
                },
                "data": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "update": {
                                "type": "object",
                                "properties": {
                                    "bids": {
                                        "type": "array",
                                        "items": {
                                            "type": "array",
                                            "minItems": 3,
                                            "maxItems": 3,
                                            "items": [
                                                {"type": "string"},
                                                {"type": "string"},
                                                {"type": "string"}
                                            ]
                                        }
                                    },
                                    "asks": {
                                        "type": "array",
                                        "items": {
                                            "type": "array",
                                            "minItems": 3,
                                            "maxItems": 3,
                                            "items": [
                                                {"type": "string"},
                                                {"type": "string"},
                                                {"type": "string"}
                                            ]
                                        }
                                    }
                                },
                                "required": ["bids", "asks"]
                            },
                            "t": {"type": "integer"},
                            "tt": {"type": "integer"},
                            "u": {"type": "integer"},
                            "pu": {"type": "integer"}
                        },
                        "required": ["update", "t", "tt", "u", "pu"]
                    }
                }
            },
            "required": ["instrument_name", "subscription", "channel", "depth", "data"]
        }
    },
    "required": ["id", "method", "code", "result"]
}
