import os
from pathlib import Path


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable is not set: {name}")
    return value


def require_secret(name: str) -> str:
    path = Path("/run/secrets") / name

    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise RuntimeError(f"Required secret is not available: {name}") from exc

    if not value:
        raise RuntimeError(f"Required secret is empty: {name}")

    return value


STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "endpoint_url": require_env("S3_ENDPOINT_URL"),
            "region_name": os.environ.get("S3_REGION", "auto"),
            "bucket_name": require_env("S3_BUCKET_NAME"),
            "access_key": require_env("S3_ACCESS_KEY_ID"),
            "secret_key": require_secret("s3_secret_access_key"),
            "location": os.environ.get("S3_MEDIA_PREFIX", "media"),
            "signature_version": "s3v4",
            "default_acl": None,
            "querystring_auth": True,
        },
    },
}
