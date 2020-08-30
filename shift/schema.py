# Set to automatically break when the API version is incremented.
# Make sure you check the new output to see what data has changed before updating.

SHIFT_API_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["meta", "codes"],
        "properties": {
            "meta": {
                "type": "object",
                "required": ["version", "generated"],
                "properties": {
                    "version": {"const": "1.0"},
                    "generated": {
                        "type": "object",
                        "required": ["epoch"],
                        "properties": {
                            "epoch": {"type": "string"}
                        }
                    }
                }
            },
            "codes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["code", "game", "platform", "reward", "expires", "link"],
                    "properties": {
                        "code": {"type": "string"},
                        "game": {"type": "string"},
                        "platform": {"type": "string"},
                        "reward": {"type": "string"},
                        "expires": {"type": "string"},
                        "link": {"type": "string"}
                    }
                }
            }
        }
    }
}
