# Cost note

Rough, order-of-magnitude, us-east-1, on-demand. Check current pricing before relying on any number.

| Part | Driver | Rough cost |
|---|---|---|
| Bedrock Nova Pro | input and output tokens; a story is about 700 output tokens | the dominant cost, still a fraction of a cent per story at published Nova Pro rates |
| Lambda | 256 MB, a few seconds per call | negligible |
| S3 | a few KB per story | negligible |
| DynamoDB | pay-per-request, one write per story | negligible |

Takeaway: the model call is the whole bill. Levers, in order: shorter stories, a smaller Nova model (Lite or Micro) if quality is acceptable, caching popular theme and setting combinations, and a daily budget alarm. The lab itself ran in a free temporary account.
