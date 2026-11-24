import json

from local.mock_clients import MockBedrock, MockS3, MockTable
from story_gen import StoryGenerator, handler


def setup(responder=None):
    s3, table = MockS3(), MockTable()
    handler.set_generator(StoryGenerator(MockBedrock(responder), s3, table, "b"))
    return s3, table


def test_handler_success_returns_uid_title_key():
    s3, table = setup()
    r = handler.lambda_handler({"character": "Omar the camel", "theme": "patience", "setting": "Riyadh"}, None)
    body = json.loads(r["body"])
    assert r["statusCode"] == 200 and set(body) == {"uid", "title", "s3_key"}
    assert body["uid"] in table.items and ("b", body["s3_key"]) in s3.objects


def test_handler_works_with_empty_event_like_the_lab_test_event():
    setup()
    assert handler.lambda_handler({}, None)["statusCode"] == 200
    assert handler.lambda_handler(None, None)["statusCode"] == 200


def test_bad_model_output_is_502_and_hides_details():
    setup(lambda p: "not json")
    r = handler.lambda_handler({}, None)
    assert r["statusCode"] == 502 and "Traceback" not in r["body"]


def test_unexpected_error_is_500_without_internals():
    class Boom:
        def generate(self, *a):
            raise RuntimeError("secret-table-name")
    handler.set_generator(Boom())
    r = handler.lambda_handler({}, None)
    assert r["statusCode"] == 500 and "secret" not in r["body"]
