Almost nobody I talk to can say what one feature costs to ship. That is why the AI invoice is unanswerable.

Fixed-cost tooling trained us badly. A JetBrains seat, a CI plan, a design license: pay once a year, forecast by headcount, never think about it again. Usage-based agent pricing scales with effort instead, so the line moves every month and nobody can explain why.

At Spotify I chaired the Productivity Engineering Technical Steering Group across six teams, and the thing that finally moved the number (30% fewer non-business-focused dev cycles) was not a better dashboard. It was picking a unit of work the business recognized and measuring the whole window around it.

Seats, tokens, and PR counts all fail as denominators. Seats measure adoption. Tokens measure consumption. PR count goes up while shipped scope stays flat, because agents change how engineers package work, not how much of it lands.

Try one feature instead. An optional date-of-birth field on the user profile: requirements, the 18+ rule, a migration, API validation, frontend, rollout.

→ Baseline: 5 engineer-days, roughly $4,000 fully loaded
→ With agents: 3 engineer-days, roughly $2,400
→ Break-even agent spend: $1,600 across three days

Almost nobody hits $1,600 in three days of focused feature work. And even at break-even you still shipped two days earlier with two engineer-days back in the queue.

Two things that break the math. Agents running overnight decouple elapsed days from engineer hours, so track net hours or you will credit the tool for an extended work week. And an engineer running three tickets at once has genuinely expanded capacity, but you can no longer divide their day cleanly across features.

Nobody asks the JetBrains license to prove ROI. Usage-based pricing did not invent the expense, it just made it visible and variable at the same time.

Curious how other engineering leaders are attributing this. Per-feature, per-team, or still defending a per-seat line item?

Full breakdown:
