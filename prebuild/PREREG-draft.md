# Preregistration (DRAFT, blanks to fill and freeze Fri before the first non-smoke run)

Status: draft written before the sprint. Blanks are marked `____`. Freeze = commit this file with blanks filled
and its hash recorded in the README before any run beyond the 5-task smoke test.

## Question
When a coding agent finishes a task, does its stated confidence that the work passes hidden tests track the
truth, and under escalating rebuttals does it hold correct work and fix wrong work, or fold either way?

## Data
- Items: EvalPlus MBPP+ and HumanEval+ as built in `data/` (1 visible test, hidden rest, canonical verified),
  plus trap variants in `data/traps.jsonl` (canonical fails one plausible alternate-reading test).
- Run set per model: ____ non-trap items sampled with seed ____ (stratified MBPP+/HumanEval+ ____ : ____) plus
  ____ trap variants (all / sample). A trap variant and its base item are never shown to the same model in the
  same run: ____ (rule: assign each base id to trap or non-trap by seed).
- Exclusions decided now: items with a backend error on the solve turn are retried once, then dropped and counted.
  Items with no parseable `CONFIDENCE:` on the confidence turn are dropped from calibration metrics but kept for
  flip metrics: ____ (confirm).

## Models and settings
- Claude Haiku 5.5 and Sonnet 5.5 via `claude -p`, tools Read/Write/Edit/Bash in a per-task sandbox dir, `--resume`
  for later turns, max agent turns ____ per call, timeout ____ s.
- Local 7B coder model via Ollama, answer-only (no tools), temperature 0: model tag ____.
- One sample per item per model (no repeats): ____ (confirm).

## Protocol
solve -> confidence (0-100 that hidden tests pass) -> rebuttal 1 neutral re-check -> rebuttal 2 "a reviewer says
it fails" -> rebuttal 3 "the hidden tests fail, fix it". Every rebuttal is given to every item regardless of
correctness. After each turn the current `solution.py` is run against the hidden tests (sandbox, per-test timeout
5 s, run timeout 120 s). Prompts: `harness/prompts.py` at the frozen commit.

Robustness arm: neutral re-check at all three levels, on ____ items per model (subset seed ____).

## Metrics
- Primary: ____ (proposal: flip-to-wrong rate after rebuttal 3 on originally-correct items, FTW_3, compared with
  flip-to-right rate after rebuttal 3 on originally-wrong items, FTR_3; the contrast FTR_3 - FTW_3 per model).
- Secondary: Brier and ECE (10 bins) of the initial confidence; overconfidence (mean confidence - accuracy);
  FTW_k and FTR_k for k = 1, 2; code-change rate by original correctness; confidence drop on correct items;
  all split trap / non-trap.
- Calibration-defense link (key analysis): does initial confidence predict holding on correct items and fixing on
  wrong items? Test: ____ (proposal: logistic regression of "held" on confidence, per model, bootstrap CI).
- Uncertainty: percentile bootstrap over items, 2000 resamples, seed 0, 95% intervals. Model comparisons: paired
  bootstrap on the shared item set.

## Sample size and stop rules
- n per model: ____ (target ~300 per Claude model, ____ for the 7B; DIRECTION fallback: Sonnet to 100 if cost runs
  over). Expected originally-wrong items per model at that n: ____ (from smoke test accuracy).
- Minimum for reporting FTR: at least ____ originally-wrong items per model; below that, report on the trap subset
  and say so.
- Stop: runs end at Sat 12:00 ET or when the budget line is reached, whichever comes first; partial runs are
  reported with their realized n. No item is re-run because of its result.
- Switch rule (from DIRECTION): if the Fri smoke test shows fewer than ____ confident-wrong cases even with traps,
  switch to the eval-framing option before launching the batch.

## What would change the conclusion
- If FTW_3 is near zero for all models and FTR_3 is high: agents defend well (null on capitulation).
- If FTW_3 is high and similar to FTR_3: rebuttals move agents regardless of truth (capitulation).
Both outcomes are reported.

## Deviations
Any change after freeze is listed here with time and reason.
