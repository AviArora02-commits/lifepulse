# Agent Decision Flows

## Conflict policy

Complaint and safety resolution always wins over product pitch. If the life-event detector finds a baby, home, salary, or relocation signal during a failed transaction or complaint, the pitch is queued for post-resolution.

## Confidence policy

- Intent confidence below 0.72 asks one clarifying question.
- Life-event confidence below 0.55 is ignored.
- Life-event confidence 0.55 to 0.75 is queued for RM review.
- Life-event confidence above 0.75 can be shown proactively.
- Resolution confidence below 0.60 escalates.

## Escalation triggers

- Frustration score above 0.70
- Explicit human/RM request
- Compliance flag
- More than three failed attempts
- Low resolution confidence
