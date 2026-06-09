# Interview Prompt Cheat Sheet

Useful prompts for a 3-hour AI-assisted coding interview.

---

## Phase 1 — System Design (first 20 min)

```
You are a senior backend engineer helping me finish a system design
+ implementation in a 3-hour AI-assisted onsite interview.

Requirement: [paste the problem statement]

Please do NOT write code yet. Help me:
1. Define functional requirements (core features)
2. Define non-functional requirements (scale, latency, reliability)
3. Identify what's out of scope
4. Propose MVP scope with 4-5 milestones
5. Design the API endpoints
6. Design the data model
7. Recommend the tech stack and justify each choice
8. Identify the hardest technical challenge

Optimize for interview success: working code over perfect architecture.
```

---

## Phase 2 — Starting each milestone

```
Let's implement [milestone name]:
[describe what it does in one line]

Requirements:
- Keep the structure clean but minimal
- Every change must be testable
- No features beyond what's needed

After coding, explain what each file does and how to test it.
```

---

## Phase 3 — Before writing code, get the plan

```
Before writing any code, give me:
1. Which files will be created or modified
2. The exact logic flow step by step
3. Key design decisions and why
4. What the tests will cover

Do not write code yet.
```

---

## Phase 4 — Debugging errors

```
I got this error when running [command]:
[paste full error]

What is the root cause and what is the minimal fix?
Do not change anything beyond what's needed to fix this.
```

---

## Phase 5 — Writing tests

```
Write tests for [feature]. Before writing any code, list every
test case you will cover:
- happy path
- error cases
- edge cases

Then confirm with me before implementing.

Requirements:
- No real API calls (mock external services)
- No disk writes (in-memory DB)
- Each test must be independently runnable
```

---

## Phase 6 — Production / NFR discussion

```
We have finished the MVP. List all non-functional requirements
for a production version of this system and how we would
implement each one. Just the plan, no code.
```

```
Turn these NFRs into prioritized milestones. I have [X] minutes
left. Mark which ones to implement now vs. document as future work.
Each milestone must be small, testable, and self-contained.
```

---

## Phase 6.5 — MVP to Production Evolution

We have finished the MVP.

Help me evolve this system from MVP to production level.

Please analyze it layer by layer:

API layer
Database layer
Async processing / queue layer
Caching layer
Reliability and failure handling
Observability
Security and abuse protection
Deployment and scaling

For each layer, explain:

What we have in the MVP
What limitation it has
What production version should use
Whether I should implement it now or only document it
What tradeoff I should explain in code review

Optimize for a 3-hour coding interview. Do not suggest unnecessary infrastructure.

## Phase 7 — Architecture diagrams

```
Draw a high-level ASCII architecture diagram of the current
implementation. Mark any components added beyond the MVP as [V2.0].
Keep it simple — components and connections only, no details.
```

---

## Phase 8 — Gap analysis

```
Here is the reference system design for this problem: [paste or
describe]. Compare it to what we built and list every gap.
For each gap state: what we have, what they recommend, and the
priority to close it.
```

---

## Phase 9 — Explaining your decisions (interviewer asks "why")

```
Give me a one-sentence justification for each of these decisions
in our implementation:
- choice of framework
- database choice
- how we handle [specific feature]
- the tradeoff we made in [area]

Frame it as: we chose X over Y because Z. The tradeoff is A.
```

---

## Phase 10 — Wrapping up

```
Generate a concise README.md for this project covering:
1. Project overview
2. Architecture diagram
3. API endpoints
4. Design decisions and tradeoffs
5. How to run
6. Example curl commands
7. Known limitations
8. Future improvements

Goal: an interviewer can understand the full project in 2 minutes.
```

---

## Meta tips for the interview

| Situation | What to do |
|---|---|
| Unclear requirement | Ask Claude to list assumptions, confirm with interviewer |
| Running out of time | Ask Claude to prioritize: "I have 20 min left, what matters most?" |
| Interviewer asks "why" | Always explain the tradeoff, not just the choice |
| Something breaks | Paste the full error — never guess at fixes |
| Stuck on a concept | "Explain this to me like I'm explaining it to an interviewer" |
| Want to impress | Ask for production gaps proactively before the interviewer does |

---

## The one meta-prompt that ties it all together

```
I am in a 3-hour coding interview. The problem is: [problem].
Act as my senior engineering partner. At each step:
- Keep code minimal and working
- Flag tradeoffs I should mention to the interviewer
- Tell me what to implement now vs. defer
- Make sure everything is testable
```
