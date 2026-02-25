import hashlib
import jwt
from urllib.parse import urlparse, parse_qs, quote
import os
import time

# Zephyr secrets
access_key = os.environ.get("ZEPHYR_ACCESS_KEY")
secret_key = os.environ.get("ZEPHYR_SECRET_KEY")
zephyr_username = os.environ.get("ZEPHYR_USERNAME")


def _canonicalize_method(http_method: str) -> str:
    return http_method.upper()


def _canonicalize_uri(url: str, base_url: str = "") -> str:
    parsed = urlparse(url)
    path = parsed.path

    # Strip the base URL path prefix (mirrors JwtGeneratorImpl.getUri())
    if base_url:
        base_path = urlparse(base_url).path
        if path.startswith(base_path):
            path = path[len(base_path) :]

    # Remove trailing slash, default to "/" if blank
    path = path.rstrip("/") or "/"

    # Percent-encode '&' in the path (mirrors canonicalizeUri)
    path = path.replace("&", _percent_encode("&"))

    # Ensure path starts with /
    if not path.startswith("/"):
        path = "/" + path

    return path


def _canonicalize_query_params(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.query:
        return ""

    # Parse query string, preserving order of multiple values
    params = parse_qs(parsed.query, keep_blank_values=True)

    # Exclude 'jwt' parameter (as the Java code does)
    params.pop("jwt", None)

    # Sort by key, then for each key encode key=sorted_encoded_values
    parts = []
    for key in sorted(params.keys()):
        encoded_key = _percent_encode(key)
        # Sort and percent-encode each value, join multiples with ","
        encoded_values = ",".join(sorted(_percent_encode(v) for v in params[key]))
        parts.append(f"{encoded_key}={encoded_values}")

    return "&".join(parts)


def _percent_encode(s: str) -> str:
    """Does RFC 3986 percent-encoding for the provided string. It matches JwtUtil.percentEncode(). URLEncode with UTF-8

    Args:
        s: The string to encode

    Returns:
        The encoded string
    """
    if s is None:
        return ""

    encoded = quote(s, safe="")  # encode everything (no safe chars)
    encoded = encoded.replace("+", "%20")
    encoded = encoded.replace("*", "%2A")
    encoded = encoded.replace("%7E", "~")
    return encoded


def compute_qsh(http_method: str, endpoint_url: str) -> str:
    """Compute the Query String Hash (QSH) for a Zephyr/Atlassian JWT.

    Args:
        http_method: HTTP method (GET, POST, PUT, etc.)
        url: The full request URL
        base_url: The Zephyr base URL whose path prefix should be stripped

    Returns:
        Produce the canonical request string: METHOD&path&sorted_query_params
    """
    if "/public" not in endpoint_url:
        raise ValueError(
            f"Zephyr Squad endpoint URL must contain '/public'. Provided: {endpoint_url}"
        )
    base_url = endpoint_url.split("/public")[0]

    method = _canonicalize_method(http_method)
    uri = _canonicalize_uri(endpoint_url, base_url)
    query = _canonicalize_query_params(endpoint_url)
    canonical = f"{method}&{uri}&{query}"

    # SHA-256 hash, returned as lowercase hex (matches JwtUtil.computeSha256Hash).
    return hashlib.sha256(canonical.encode()).hexdigest()


def generate_zephyr_jwt(
    endpoint_url: str,
    http_method: str,
) -> str:
    """Generate JWT for Zephyr Squad API authentication.

    This is a Python translation of the Java ZFJCloudRestClient JWT generation.

    Args:
        uri: The full URI for the API request e.g. https://prod-api.zephyr4jiracloud.com/connect/public/rest/api/1.0/zql/search
        http_method: HTTP method (GET, POST, PUT, DELETE, etc.)
        access_key: Zephyr access key (defaults to ZEPHYR_ACCESS_KEY env var)
        secret_key: Zephyr secret key (defaults to ZEPHYR_SECRET_KEY env var)
        account_id: User account ID/username (defaults to ZEPHYR_ACCOUNT_ID env var)
        expiration_in_sec: JWT expiration time in seconds (default: 360)

    Returns:
        The generated JWT string
    """

    if not all([access_key, secret_key, zephyr_username]):
        raise ValueError(
            "Missing Zephyr credentials. Please set ZEPHYR_ACCESS_KEY, "
            "ZEPHYR_SECRET_KEY, and USERNAME environment variables."
        )

    qsh = compute_qsh(http_method, endpoint_url)

    # Current timestamp
    current_time = int(time.time())

    # JWT payload
    payload = {
        "sub": zephyr_username,
        "qsh": qsh,
        "iss": access_key,
        "iat": current_time,
        "exp": current_time + (60 * 6),
    }

    # Generate JWT using HS256 algorithm
    token = jwt.encode(payload, secret_key, algorithm="HS256")

    return token
