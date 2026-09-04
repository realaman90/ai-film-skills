"""Public media hosting for APIs that need URLs (Seedance / Seedream on BytePlus Ark).

Default backend: **Amazon S3** (Sept 2026). Cloudflare R2 still works if only R2_* vars are set.

Env (S3):
    ASSET_STORAGE    s3 (default) | r2 — which backend to use when both are configured
    S3_BUCKET        bucket name (required; S3_BUCKET_NAME also accepted)
    S3_ACCESS_KEY_ID / S3_SECRET_ACCESS_KEY   explicit credentials (or the standard AWS_* / AWS_PROFILE chain)
    S3_REGION        e.g. eu-north-1 (falls back to AWS_REGION / AWS_DEFAULT_REGION / boto3 default)
    S3_PREFIX        optional key prefix, default "ai-film"
    S3_PUBLIC_URL    optional CDN/base URL, e.g. https://media.example.com — if unset a presigned URL (24 h) is
                     returned, so the bucket can stay private. Set it only if the bucket/prefix is public-read.
    AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SESSION_TOKEN or AWS_PROFILE — standard boto3 credential chain.

Env (R2, legacy): R2_ACCOUNT, R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET, R2_PUBLIC_URL

CLI:
    python scripts/media_host.py upload path/to/file.png [--prefix seedance]   -> prints the URL
    python scripts/media_host.py check                                          -> verifies credentials + bucket (no values printed)
"""
import mimetypes
import os
import sys
import time

CONTENT_TYPES = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
    ".mp4": "video/mp4", ".mov": "video/quicktime", ".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4",
}


def _s3_bucket():
    return os.environ.get("S3_BUCKET") or os.environ.get("S3_BUCKET_NAME")


def backend():
    """ASSET_STORAGE=s3|r2 decides when both are configured; otherwise whichever is configured."""
    pref = (os.environ.get("ASSET_STORAGE") or "").lower()
    has_s3 = bool(_s3_bucket())
    has_r2 = bool(os.environ.get("R2_BUCKET") and os.environ.get("R2_ACCOUNT"))
    if pref == "r2" and has_r2:
        return "r2"
    if has_s3:
        return "s3"
    if has_r2:
        return "r2"
    return None


def _content_type(path):
    ext = os.path.splitext(path)[1].lower()
    return CONTENT_TYPES.get(ext) or mimetypes.guess_type(path)[0] or "application/octet-stream"


def _s3_client():
    import boto3
    region = os.environ.get("S3_REGION") or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    kw = {"region_name": region} if region else {}
    # explicit S3_* credentials (repo naming) take precedence over the ambient AWS chain
    ak = os.environ.get("S3_ACCESS_KEY_ID") or os.environ.get("AWS_ACCESS_KEY_ID")
    sk = os.environ.get("S3_SECRET_ACCESS_KEY") or os.environ.get("AWS_SECRET_ACCESS_KEY")
    if ak and sk:
        kw.update(aws_access_key_id=ak, aws_secret_access_key=sk)
    return boto3.client("s3", **kw)


def upload_public(local_path, prefix=None, expires=86400):
    """Upload a local file and return a URL an external API can fetch. None on failure (error printed, no secrets)."""
    be = backend()
    if not be:
        print("media_host: no hosting configured (set S3_BUCKET [+ S3_REGION], or R2_* vars)")
        return None
    basename = os.path.basename(local_path)
    stamp = time.strftime("%Y%m%d")
    try:
        if be == "s3":
            bucket = _s3_bucket()
            key = f"{prefix or os.environ.get('S3_PREFIX', 'ai-film')}/{stamp}/{basename}"
            s3 = _s3_client()
            s3.upload_file(local_path, bucket, key, ExtraArgs={"ContentType": _content_type(local_path)})
            public = os.environ.get("S3_PUBLIC_URL")
            if public:
                return f"{public.rstrip('/')}/{key}"
            return s3.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expires)
        else:  # r2
            import boto3
            s3 = boto3.client(
                "s3",
                endpoint_url=f"https://{os.environ['R2_ACCOUNT']}.r2.cloudflarestorage.com",
                aws_access_key_id=os.environ["R2_ACCESS_KEY"],
                aws_secret_access_key=os.environ["R2_SECRET_KEY"],
                region_name="auto",
            )
            key = f"{prefix or 'ai-film'}/{basename}"
            s3.upload_file(local_path, os.environ["R2_BUCKET"], key, ExtraArgs={"ContentType": _content_type(local_path)})
            return f"{os.environ['R2_PUBLIC_URL'].rstrip('/')}/{key}"
    except Exception as e:
        print(f"media_host: {be} upload failed: {type(e).__name__}: {str(e)[:200]}")
        return None


def check():
    be = backend()
    print(f"backend: {be or 'NONE'}")
    if be == "s3":
        try:
            s3 = _s3_client()
            bucket = _s3_bucket()
            s3.head_bucket(Bucket=bucket)
            ident = None
            try:
                import boto3
                ident = boto3.client("sts").get_caller_identity()
            except Exception:
                pass
            print(f"bucket: {bucket} reachable | region: {s3.meta.region_name} | public_url: {'set' if os.environ.get('S3_PUBLIC_URL') else 'unset -> presigned URLs'}"
                  + (f" | account: ...{ident['Account'][-4:]}" if ident else ""))
            return 0
        except Exception as e:
            print(f"S3 check failed: {type(e).__name__}: {str(e)[:200]}")
            return 1
    if be == "r2":
        print("R2 configured (legacy)")
        return 0
    return 1


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "check":
        sys.exit(check())
    if len(sys.argv) >= 3 and sys.argv[1] == "upload":
        prefix = None
        if "--prefix" in sys.argv:
            prefix = sys.argv[sys.argv.index("--prefix") + 1]
        url = upload_public(sys.argv[2], prefix)
        if not url:
            sys.exit(1)
        print(url)
        sys.exit(0)
    print(__doc__)
    sys.exit(2)
