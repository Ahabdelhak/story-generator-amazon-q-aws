# Flow

1. Caller sends `{character, theme, setting}` (all optional; defaults apply).
2. `clean_field` trims and caps each value.
3. `build_prompt` wraps them as quoted story details and asks for JSON only.
4. Bedrock `invoke_model` (Nova Pro) returns text; `parse_story` turns it into title and story.
5. `put_object` writes `uid.txt` to S3.
6. `put_item` writes uid, title, bucket, key, inputs, word count and timestamp to DynamoDB.
7. Lambda returns `{uid, title, s3_key}` (200). Bad model output gives 502, anything else 500.
