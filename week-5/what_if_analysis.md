# Week 5 What If Analysis

Baseline assumptions use 2,000 requests/day, 1,200 input tokens/request, 300 output tokens/request, and a 20% safety margin.

| Scenario | Changed assumption | Estimated result | Effect |
| --- | --- | --- | --- |
| Baseline | Sample `.env` values | $1.44/day and $43.20/month before margin; $51.84/month with margin | RPM and TPM pass. Daily budget passes, but the $50 monthly budget needs review after the margin. |
| More users | Requests/day: 2,000 → 4,000 | $2.88/day and $86.40/month before margin | Daily and monthly budgets fail after applying the margin; daily token volume doubles. Peak RPM/TPM stay the same in this scenario because peak requests/minute was held constant. |
| Longer context | Input tokens/request: 1,200 → 2,800 | $2.40/day; peak total TPM with margin: 111,600 | TPM exceeds the illustrative 100,000 limit; daily and monthly budget checks also fail after margin. |
| Traffic spike | Peak requests/minute: 30 → 51 | Peak RPM with margin: 61.2 | RPM exceeds the illustrative 60 RPM limit; peak TPM is 91,800 and remains under its configured limit. |
| Longer answers reduced | Output tokens/request: 300 → 150 | $1.08/day and $32.40/month before margin; 48,600 peak total TPM with margin | Cost and TPM decrease; both budget checks pass after margin. |

## Recommendation

With the supplied rates and traffic assumptions, revise the monthly budget to at least $51.84 for the 20% planning margin, or reduce expected usage/cost before building. Confirm actual model prices and provider quota definitions before using this estimate for a launch decision.
