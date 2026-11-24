"""Same shape as the lab: Lambda + S3 + DynamoDB + Bedrock, but as code you can redeploy."""
import pathlib

import aws_cdk as cdk
from aws_cdk import aws_dynamodb as ddb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
from constructs import Construct

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL_ID = "amazon.nova-pro-v1:0"


class StoryStack(cdk.Stack):
    def __init__(self, scope: Construct, cid: str, **kw):
        super().__init__(scope, cid, **kw)
        bucket = s3.Bucket(self, "StoryBucket", block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                           encryption=s3.BucketEncryption.S3_MANAGED, enforce_ssl=True,
                           removal_policy=cdk.RemovalPolicy.DESTROY, auto_delete_objects=True)
        table = ddb.Table(self, "StoryTable",
                          partition_key=ddb.Attribute(name="uid", type=ddb.AttributeType.STRING),
                          billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
                          removal_policy=cdk.RemovalPolicy.DESTROY)
        fn = _lambda.Function(
            self, "StoryTeller", runtime=_lambda.Runtime.PYTHON_3_13,
            handler="story_gen.handler.lambda_handler",
            code=_lambda.Code.from_asset(str(ROOT), exclude=["*", "!story_gen", "!story_gen/*.py"]),
            timeout=cdk.Duration.seconds(60),  # the lab's 15s is tight for a 500-word generation
            memory_size=256,
            environment={"BUCKET_NAME": bucket.bucket_name, "TABLE_NAME": table.table_name},
        )
        bucket.grant_put(fn)      # PutObject only
        table.grant_write_data(fn)  # PutItem only
        fn.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=[f"arn:aws:bedrock:{self.region}::foundation-model/{MODEL_ID}"]))
