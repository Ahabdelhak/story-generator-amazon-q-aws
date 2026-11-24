# Decision log

Each row: what the lab-generated code did, what this repo does instead, and why.

| # | Lab / Amazon Q draft | This repo | Why |
|---|---|---|---|
| 1 | Title found with `story.split('Title:')[1]` | Ask Nova for `{"title","story"}` JSON and `json.loads` it (`parse_story`) | The model answered in JSON, so the lab run stored "No Title". Parsing structure beats string-splitting prose. |
| 2 | `uid = md5(title)[:10]` | `uuid4().hex[:10]` | A title hash is not random and made every story collide on the same S3 key and DynamoDB item. Test: `test_two_stories_with_same_inputs_do_not_collide`. |
| 3 | `maxTokens: 512` | `1024` | A 500-word story is roughly 650 tokens; 512 risks cutting the JSON mid-string. Truncated output raises `StoryParseError` and stores nothing. Not observed in the lab, a risk found by reading the code. |
| 4 | Fixed prompt, no inputs | `build_prompt(character, theme, setting)` | The business problem is personalisation from user inputs. |
| 5 | Inputs would go straight into the prompt | `clean_field`: trim, cap at 60 chars, strip quotes; inputs quoted and labelled "story details only" | Cheap first defence against prompt injection. Not a guarantee; see limitations. |
| 6 | Error returned `str(e)` with status 501 | 502 for bad model output, 500 otherwise, generic bodies, details only in logs | Do not leak table names or stack traces to callers. |
| 7 | Clients created inside the handler | Clients injected into `StoryGenerator` | Runs offline against mocks, 24 tests, no account needed. |
| 8 | S3 write then DynamoDB write, no handling | Same order, documented | If DynamoDB fails the S3 object is orphaned. Acceptable for a story archive; a delete-on-failure or Step Functions saga is the upgrade. |
| 9 | 15 s Lambda timeout | 60 s in CDK | Generation of a long story can exceed 15 s; Lambda max is 15 min. |
| 10 | Lab IAM role (broad) | CDK grants `PutObject`, `PutItem` and `InvokeModel` on one model ARN only | Least privilege; asserted in `test_infra.py`. |

## What Amazon Q was good and bad at

Good: boilerplate lines from a plain comment (Bedrock client, environment variables, `put_object`). Bad: it chose naive logic where the data shape mattered (title parsing, uid), placed code at the comment's indentation (outside the `try`), and stopped answering on the DynamoDB comment after several retries. Treat it as a fast first draft that needs review and tests.

## Known limitations

- Moderation is prompt-level only. A children's product needs an output check (for example Bedrock Guardrails) before publishing stories.
- No auth or rate limit in front of the Lambda. Add API Gateway with an authorizer and throttling before exposing it.
- The real-AWS path (`scripts/run_on_aws.py`, `cdk deploy`) has not been run by the author. The lab ran the original Lambda for real; the code in this repo is tested against mocks only.
