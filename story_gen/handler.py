"""Lambda entry point. BUCKET_NAME and TABLE_NAME come from environment variables."""
import json
import logging
import os

from .core import StoryGenerator, StoryParseError

log = logging.getLogger()
log.setLevel(logging.INFO)
_generator = None


def set_generator(gen):
    """Tests and local runs inject a generator built from mock clients."""
    global _generator
    _generator = gen


def _build():
    import boto3  # imported lazily so unit tests need no AWS libraries
    return StoryGenerator(
        bedrock=boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1")),
        s3=boto3.client("s3"),
        table=boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"]),
        bucket=os.environ["BUCKET_NAME"],
    )


def lambda_handler(event, context):
    global _generator
    event = event if isinstance(event, dict) else {}
    try:
        _generator = _generator or _build()
        item = _generator.generate(event.get("character"), event.get("theme"), event.get("setting"))
        body = {k: item[k] for k in ("uid", "title", "s3_key")}
        return {"statusCode": 200, "body": json.dumps(body)}
    except StoryParseError as exc:
        log.warning("bad model output: %s", exc)
        return {"statusCode": 502, "body": json.dumps({"error": "story generation failed, try again"})}
    except Exception:  # never leak internals to the caller
        log.exception("unhandled error")
        return {"statusCode": 500, "body": json.dumps({"error": "internal error"})}
