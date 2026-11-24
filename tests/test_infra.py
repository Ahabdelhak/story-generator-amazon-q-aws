import sys, pathlib
import aws_cdk as cdk
from aws_cdk.assertions import Match, Template

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "infra"))
from story_stack import StoryStack  # noqa: E402

t = Template.from_stack(StoryStack(cdk.App(), "T", env=cdk.Environment(region="us-east-1", account="111111111111")))


def test_resources_exist():
    t.resource_count_is("AWS::DynamoDB::Table", 1)
    t.has_resource_properties("AWS::DynamoDB::Table", {"KeySchema": [{"AttributeName": "uid", "KeyType": "HASH"}]})
    t.has_resource_properties("AWS::Lambda::Function", {"Runtime": "python3.13", "Timeout": 60,
        "Environment": {"Variables": {"BUCKET_NAME": Match.any_value(), "TABLE_NAME": Match.any_value()}}})


def test_bucket_is_private_and_encrypted():
    t.has_resource_properties("AWS::S3::Bucket", {"PublicAccessBlockConfiguration": {
        "BlockPublicAcls": True, "BlockPublicPolicy": True, "IgnorePublicAcls": True, "RestrictPublicBuckets": True}})


def test_bedrock_permission_is_scoped_to_one_model():
    t.has_resource_properties("AWS::IAM::Policy", {"PolicyDocument": {"Statement": Match.array_with([
        {"Action": "bedrock:InvokeModel", "Effect": "Allow",
         "Resource": "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0"}])}})


def test_no_wildcard_iam_actions():
    for pol in t.find_resources("AWS::IAM::Policy").values():
        for st in pol["Properties"]["PolicyDocument"]["Statement"]:
            acts = st["Action"] if isinstance(st["Action"], list) else [st["Action"]]
            assert not any(a == "*" or a.endswith(":*") for a in acts)
