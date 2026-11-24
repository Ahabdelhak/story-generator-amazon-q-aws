"""In-memory stand-ins for Bedrock, S3 and DynamoDB. No AWS account or credentials needed."""
import io
import json
import re


class MockBedrock:
    def __init__(self, responder=None):
        self.responder = responder or self._default
        self.calls = []

    @staticmethod
    def _default(prompt):
        pick = lambda label: re.search(rf'{label}: "(.*)"', prompt).group(1)
        c, t, s = pick("Character"), pick("Theme"), pick("Setting")
        story = (f"Once upon a time, {c} lived in {s}. One morning {c} learned a little "
                 f"something about {t}. By sunset everyone had shared a smile, and {c} "
                 "went home happy. The end.")
        return json.dumps({"title": f"{c.title()} and the Gift of {t.title()}", "story": story})

    def invoke_model(self, modelId, body):
        req = json.loads(body)
        prompt = req["messages"][0]["content"][0]["text"]
        self.calls.append(req)
        out = {"output": {"message": {"content": [{"text": self.responder(prompt)}]}}}
        return {"body": io.BytesIO(json.dumps(out).encode())}


class MockS3:
    def __init__(self):
        self.objects = {}

    def put_object(self, Bucket, Key, Body):
        self.objects[(Bucket, Key)] = Body


class MockTable:
    def __init__(self):
        self.items = {}

    def put_item(self, Item):
        self.items[Item["uid"]] = Item
