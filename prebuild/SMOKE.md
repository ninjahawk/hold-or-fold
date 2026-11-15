# Smoke test and access checks (pre-build, dry run)

Everything here is a **plumbing check, not a result**. No accuracy, calibration or flip numbers from these runs are
findings (n = 5 per backend at most, and most rows below are the oracle). The sprint rule allows no experiment
before Fri 2026-11-13 18:00 ET beyond a 5-task smoke test per backend.

## What ran (2026-11-11)

| Check | Backend | Status | Evidence |
|---|---|---|---|
| Full protocol end to end on real items (solve, confidence, 3 rebuttals, hidden-test scoring, scorer) | oracle (canonical / reference solution, no model) | done: 5 items (4 MBPP+, 1 trap), 25 turns, 0 `CONFIDENCE:` parse failures, 0 exec errors | `out/smoke/oracle.jsonl`, `out/smoke/oracle_summary.json` |
| `claude -p` on the Windows host: per-task sandbox dir as cwd, tool use (Write + Bash ran `python hello.py`), `--output-format json` with `session_id`, `usage`, `total_cost_usd` | Haiku 5.5 | done: 1 access-check call (not a smoke turn) | numbers below |
| `ClaudeCLIBackend` isolation (`--setting-sources ""`, `--strict-mcp-config`, user hooks re-applied via `--settings`) | Haiku 5.5 | done: a local guard hook still refuses an unauthorised launch with the isolated command line (0 tokens), and the backend reports it as `blocked by hook` and stops the run | unit tests + host check |
| 5-task smoke, full protocol (run from the authorised host runner, 2026-11-11 11:16-11:24 ET) | Haiku 5.5, Sonnet 5.5 | done: 5 items each (4 MBPP+, 1 trap), 25 turns each, 0 backend errors, 0 exec errors, 0 of 20 `CONFIDENCE:` parse failures per model; turns 2-5 of every item resumed the same CLI session | `out/smoke/haiku.jsonl`, `out/smoke/sonnet.jsonl`, `out/smoke/*_summary.json`, `out/smoke/stats.json` |
| 5-task smoke, answer-only | 7B local model (Ollama) | **open** (see Open) | |

## Plumbing bugs fixed (each has a test in `tests/test_runner.py`)

1. Prompt was passed in argv: multi-line prompts with quotes hit Windows command-line quoting and the 32k
   command-line limit. Now sent on stdin (`test_claude_cli_command_shape`).
2. User-level Claude Code settings leaked into the model under test (user CLAUDE.md, model and effort overrides,
   plugins, MCP servers). Runs are now isolated (`--setting-sources ""`, `--strict-mcp-config`); only the user's
   hooks are re-applied, so local guards keep working (`test_claude_cli_isolation_keeps_user_hooks`).
3. A call refused by a hook came back as a normal reply with rc 0, and would have been scored as a model turn
   with no solution. It is now `backend_error = "blocked by hook"`, and the run stops with nothing written
   (`test_claude_cli_parse_usage_and_errors`, `test_blocked_backend_stops_run_and_writes_nothing`).
4. Error results (`is_error`, `subtype` other than `success`, e.g. `error_max_turns`) and non-object JSON are now
   flagged instead of passing as replies (`test_claude_cli_parse_usage_and_errors`).
5. Token use was not recorded. Every transcript line now has `usage` (input, output, cache-creation, cache-read,
   thinking tokens, internal turns, duration); `harness/smoke_stats.py` aggregates it, counts `CONFIDENCE:` parse
   failures and projects the batch (`test_smoke_stats_counts_parse_failures`).
6. The `claude` subprocess now starts with `CREATE_NO_WINDOW` on Windows, so no console window can appear.
7. (pre-build 2b) The transcript did not record which CLI session a turn ran in, so `--resume` could not be audited
   from the data. Each line's `usage` now carries `session_id` and `resumed_from`
   (`test_claude_cli_records_session_and_resume`). Haiku ran before this fix; its resume was checked instead from
   the CLI's own session files (one session file per item, 5 prompts each, one session id). Sonnet's transcript
   shows it directly: per item, turn 0 has `resumed_from = null` and turns 1-4 resume the turn-0 session id.

`pytest tests`: 28 passed on the Windows host (2026-11-11).

## Per-call latency and tokens (smoke, plumbing check only)

Source: `out/smoke/stats.json` (`python -m harness.smoke_stats ... --parallel 4`), 25 turns per model, means per
turn. These are **plumbing checks, not results**: n = 5 items, the sprint is not open, and nothing about accuracy,
calibration or flips may be read from them. Wall s is the full `claude -p` round trip (process start included).
Turn 0 is the expensive one (~8.2k Haiku / ~6.8k Sonnet cache-write tokens for the fresh session); later turns
add a few hundred to ~2k.

| Backend | Wall s / turn (mean, median, max) | Output tok (of which thinking) | Cache-read tok | Cache-write tok | Input tok | API-equivalent USD / turn | `CONFIDENCE:` parse failures |
|---|---|---|---|---|---|---|---|
| Haiku 5.5 | 5.4, 5.2, 9.7 | 710 (259) | 41,630 | 2,341 | 3 | 0.0041 | 0 of 20 |
| Sonnet 5.5 | 6.5, 5.8, 11.4 | 491 (138) | 39,307 | 1,856 | 5 | 0.054 | 0 of 20 |
| 7B (Ollama) | not measured | | | | | | |

Smoke totals (API-equivalent, as reported by the CLI): Haiku $0.10, Sonnet $1.36, for 25 turns each.

## Projected batch (planned: ~300 items x 5 turns per model = 1,500 turns each)

Linear scale-up of the smoke means (stats.json `projection`). Parallel 4 assumes no rate-limit stalls, which the
smoke (sequential) did not test.

| Backend | Sequential wall-clock | At 4 in parallel | Tokens | API-equivalent USD |
|---|---|---|---|---|
| Haiku 5.5 | ~2.3 h | ~0.6 h | 62.4M cache-read, 3.5M cache-write, 1.06M output, <0.01M input | ~6 |
| Sonnet 5.5 | ~2.7 h | ~0.7 h | 59.0M cache-read, 2.8M cache-write, 0.74M output, <0.01M input | ~81 |
| 7B local | not measured | 1 (single GPU) | n/a | 0 |

Plan meter (the plan, not the API, pays for these runs): weekly 44% before (11:16 ET) and 44% after (11:25 ET);
the 5-hour meter went 33% -> 34% over the whole job, which also includes the orchestrating session. The meter
reads in whole percent, so 50 smoke turns cost under ~1 point of the 5-hour window. A 1,500-turn batch is 30x one
model's smoke; the honest bound from this resolution is "up to ~30 points of a 5-hour window per model, likely far
less for Haiku". Sonnet costs ~13x Haiku per turn in API terms, so if plan usage tracks API price, Sonnet dominates.

Window fit: Fri 18:00 to Sat 12:00 ET is 18 h; both Claude models need ~1.3 h of wall-clock at 4 parallel workers.
Recommended: run Haiku first in its own window, read the meter after ~100 items, then size Sonnet's share
(split it across two 5-hour windows if the Haiku delta implies Sonnet would cross 80%). 7B runs on the GPU
alongside (no Claude plan use).

## Open

- **OllamaBackend + 7B model** (qwen2.5-coder:7b, temperature 0, answer-only): untouched, GPU booked; separate
  short job (17:55 ET).
- **Plan-meter cost per batch** is only bounded (meter resolution is 1 point; see above). Measure it on the
  first ~100 Haiku items of the real run.
- **Parallel 4 under rate limits** not exercised (smoke was sequential).
- Each `claude -p` call leaves a session file under `~/.claude/projects/C--Users-...-Temp-task-*`. Harmless
  (they are the resume audit trail), but 300 items x 2 Claude models will leave ~600 such folders; clean up after the sprint.
