"""Run the full flow locally: python -m local.run_local "Layla the owl" friendship "a desert oasis" """
import json
import sys

from local.mock_clients import MockBedrock, MockS3, MockTable
from story_gen import StoryGenerator


def main(argv):
    s3, table = MockS3(), MockTable()
    gen = StoryGenerator(MockBedrock(), s3, table, bucket="local-story-bucket")
    item = gen.generate(*(argv[1:4] + [None] * 3)[:3])
    print("DynamoDB item:\n" + json.dumps(item, indent=2))
    (bucket, key), body = next(iter(s3.objects.items()))
    print(f"\nS3 object s3://{bucket}/{key}:\n{body.decode()}")


if __name__ == "__main__":
    main(sys.argv)
