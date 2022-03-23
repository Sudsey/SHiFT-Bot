GUILD_CONFIGS_SCHEMA = {
    "type": "array",
    "items": {}
}

GUILD_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["guild_id", "news_channel_id"],
    "properties": {
        "game_pattern": {"type": "string"},
        "guild_id": {"type": "integer"},
        "command_channel_id": {"type": "integer"},
        "news_channel_id": {"type": "integer"},
        "news_role_id": {"type": "integer"},
        "embed_emoji": {"type": "string"},
    }
}

POST_HISTORY_SCHEMA = {
    "type": "object",
    "required": ["start_time", "codes"],
    "properties": {
        "start_time": {"type": "string"},
        "codes": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

SHIFT_API_SCHEMA = {
    "type": "array",
    "items": {}
}

SHIFT_API_DATA_SCHEMA = {
    "type": "object",
    "required": ["meta", "codes"],
    "properties": {
        "meta": {},
        "codes": {
            "type": "array",
            "items": {}
        }
    }
}

# Set to automatically break when the API version is incremented.
# Make sure you check the new output to see what data has changed before updating.
SHIFT_API_METADATA_SCHEMA = {
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
}

SHIFT_API_CODE_SCHEMA = {
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
