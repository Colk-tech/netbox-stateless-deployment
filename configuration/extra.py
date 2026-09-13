import os


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable is not set: {name}"
        )
    return value


STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "endpoint_url": require_env("S3_ENDPOINT_URL"),
            "region_name": os.environ.get("S3_REGION", "auto"),
            "bucket_name": require_env("S3_BUCKET_NAME"),
            "access_key": require_env("S3_ACCESS_KEY_ID"),
            "secret_key": require_env("S3_SECRET_ACCESS_KEY"),
            "location": os.environ.get("S3_MEDIA_PREFIX", "media"),
            "signature_version": "s3v4",
            "default_acl": None,
            "querystring_auth": True,
        },
    },
}
