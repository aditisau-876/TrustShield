from urllib.parse import urlsplit, urlunsplit, unquote
import tldextract


def normalize_url(url: str) -> str:

    if not isinstance(url, str):
        return ""

    url = url.strip()

    if not url:
        return ""

    # Add scheme when absent
    if "://" not in url:
        url = "http://" + url

    parts = urlsplit(url)

    scheme = parts.scheme.lower()
    hostname = parts.hostname.lower() if parts.hostname else ""

    if not hostname:
        return ""

    # Remove default ports
    port = parts.port

    if port:
        if (scheme == "http" and port == 80) or \
           (scheme == "https" and port == 443):
            netloc = hostname
        else:
            netloc = f"{hostname}:{port}"
    else:
        netloc = hostname

    path = unquote(parts.path)

    if path == "/":
        path = ""

    # Keep query because malicious URLs often encode
    # important indicators there
    normalized = urlunsplit(
        (
            scheme,
            netloc,
            path,
            parts.query,
            ""
        )
    )

    return normalized


def extract_domain(url: str) -> str:

    normalized = normalize_url(url)

    if not normalized:
        return ""

    parts = urlsplit(normalized)

    return parts.hostname.lower() if parts.hostname else ""


def extract_registered_domain(url: str) -> str:

    domain = extract_domain(url)

    if not domain:
        return ""

    extracted = tldextract.extract(domain)

    if not extracted.domain or not extracted.suffix:
        return domain

    return f"{extracted.domain}.{extracted.suffix}"