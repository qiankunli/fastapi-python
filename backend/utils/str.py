import uuid6


def uuid7_str() -> str:
    return str(uuid6.uuid7())


def uuid7_hex() -> str:
    return uuid6.uuid7().hex
