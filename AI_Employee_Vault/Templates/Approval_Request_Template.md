---
type: approval_request
action: [action_type]
created: [ISO timestamp]
expires: [ISO timestamp + 24 hours]
status: pending
---

# Approval Required: [Action Description]

## Request Details

- **Action Type:** [e.g., send_email, make_payment, post_social]
- **Requested By:** AI Employee (Claude Code)
- **Created:** [Timestamp]
- **Expires:** [Timestamp + 24 hours]

---

## What Needs Approval

[Detailed description of the action to be taken]

### Details

| Field | Value |
|-------|-------|
| [Field 1] | [Value 1] |
| [Field 2] | [Value 2] |
| [Field 3] | [Value 3] |

---

## Why This Requires Approval

[Explanation of why this action needs human review]

---

## Risk Assessment

- **Reversibility:** [Can this be undone?]
- **Impact:** [What's the potential impact?]
- **Confidence:** [AI confidence level]

---

## To Approve

1. Review the details above
2. Move this file to `/Approved` folder
3. The AI Employee will execute the action

## To Reject

1. Move this file to `/Rejected` folder
2. Optionally add a note explaining why

## To Request Changes

1. Edit this file with your modifications
2. Move back to `/Pending_Approval`

---

*This approval request will auto-expire after 24 hours*
