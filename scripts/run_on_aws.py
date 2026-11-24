"""Run the REAL flow in YOUR account (after `cdk deploy`):
   BUCKET_NAME=... TABLE_NAME=... python scripts/run_on_aws.py "Layla the owl" friendship "an oasis"
Needs bedrock:InvokeModel on Nova Pro (enable model access first), s3:PutObject, dynamodb:PutItem."""
import json, os, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import boto3
from story_gen import StoryGenerator

region = os.environ.get("AWS_REGION", "us-east-1")
gen = StoryGenerator(boto3.client("bedrock-runtime", region_name=region), boto3.client("s3"),
                     boto3.resource("dynamodb", region_name=region).Table(os.environ["TABLE_NAME"]),
                     os.environ["BUCKET_NAME"])
item = gen.generate(*(sys.argv[1:4] + [None] * 3)[:3])
print(json.dumps(item, indent=2))
