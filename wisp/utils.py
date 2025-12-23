from urllib.parse import urlparse


def is_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in ("http", "https") and parsed.netloc != ""
    except Exception:
        return False
