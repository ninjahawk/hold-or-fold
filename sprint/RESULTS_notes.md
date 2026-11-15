## Deviations from the preregistration and from the preexisting code

- D1-D3 (before the freeze): as listed in `PREREG.md` (Linux env stripping, retry-once-then-drop, sharded runner).
- D4 (operational, after the freeze): the Sonnet main arm was stopped by the job runner on Fri 11-13 23:33 ET (the
  compute plan's 5-hour usage window was full) after 93 complete items, with no partial item in the files. It was
  resumed Sat 11-14 07:49 ET with the same runner; completed items were skipped, none was re-run, and no item was
  selected by its result. Both main arms finished before the preregistered stop time (Sat 12:00 ET); the
  meter log above shows every block check.
- D5 (analysis added after the freeze, not preregistered): the sandbox access audit and the sensitivity analysis
  without non-clean items. Reason: a Haiku reply said it had found a local data file and declined to open it. The
  audit found no hidden-test content reaching any agent from a file, and the sensitivity tables match the
  main tables within their CIs. The robustness-arm sessions were not audited.
- D6 (exploratory, as the prereg allows): the "degenerate-input trap" group is defined by a fixed regex over the
  trap rationales in `analyze.py` (`DEGEN`); the confidence bands of `fig_link.py` (<80, 80-89, >=90) were fixed
  before the Sonnet data were seen.
- D7 (figure only): the frozen scorer's `summarize()` crashes on a subset with no non-trap items, so
  `plots.py` relabels trap items as non-trap for the trap-only figure; no metric is affected.
- D8 (audit join): two items have identical solve prompts (`mbppplus/569`, `mbppplus/104#trap`), so the audit joins
  299 session logs per model to items; both were classed clean.
- D9 (analysis added Sat 11-14 after an internal red-team review, EXPLORATORY): `redteam_analysis.py` (sections
  A-L above: preregistered rules applied, Holm-corrected confirmatory family, paired by subset, within-pair, control
  vs main Fisher tests, capitulation split, measurement checks, recall sensitivity, difficulty covariates, stratified
  bootstrap, valid-draw counts, trap kinds, re-execution of 1200 scored solutions). No transcript was changed and no
  model was called. `recount.py` was extended to check the link AUROCs, paired differences and red-team counts.
- D10 (reporting fixes, same review): `analyze.py --tables-only` renders a slope as "not estimable" when an outcome
  class has fewer than 5 items (the PREREG rule; the robustness tables had printed "nan [CI]") and shows how many
  bootstrap draws were estimable; the abstract sentences are generated with data-driven wording (previously fixed
  strings); the old candidate headline about trap ECE and the pooled Sonnet-Haiku overconfidence gap was dropped
  (trap-driven; see REDTEAM.md). Figures: `figs_final.py` (new hero and reliability/defense figures), `fig_link.py`
  (labels, hollow markers for n < 5).

## Limitations (exact sentences for the Limitations section; numbers from `out/redteam.json` / `out/results.json`)

- L1. We did not measure how many wrong solutions could be fixed at all without seeing a failing test (no fresh re-solve or informative-feedback baseline), so FTR_3 is not by itself evidence of poor updating; most originally-wrong solutions were near misses (median 97% of hidden tests passed for both models).
- L2. The 40 trap items were hand-written before the sprint and checked only mechanically (the canonical solution fails the added test; an alternate reference solution passes the visible test, every original hidden test and the added test; 41 candidates were rejected); no human rated whether each prompt supports the alternate reading, so trap-subset calibration measures confidence under specification ambiguity rather than overconfidence on clear tasks.
- L3. Each item was sampled once per model, so the calibration-defense link compares items, not samples of the same item, and may partly reflect item difficulty; with difficulty covariates the held-when-correct slope stays positive for both models, but those fits are fragile (estimable in 1201 and 1587 of 2000 bootstrap draws).
- L4. Both models come from one family (Claude Haiku 5.5 and Sonnet 5.5) and the tasks are single-function MBPP+ and HumanEval+ problems solved with tool access; results may not transfer to other model families or to multi-file software-engineering tasks, and the planned local 7B model was not run.
- L5. The control arm is a separate run with fresh solves and only 11 originally-wrong items per model; it supports the claim that repeated neutral re-checking alone fixes little (Fisher p = 0.015 for Haiku and 0.081 for Sonnet against the main arm's rebuttal-3 fix rate), and it cannot separate the claim that the code fails from the instruction to fix it.
- L6. In the escalating ladder, rebuttal strength and position are confounded; no arm presents the strongest rebuttal first.
- L7. Originally-wrong non-trap items were not audited by hand for benchmark test quirks (type strictness, float handling, underspecified prompts), so some may be unfixable without seeing the hidden test.
- L8. The benchmarks are public: in 44 Haiku and 31 Sonnet items the agent typed two or more hidden-test inputs into its own checks, likely from memory; removing each model's own such items changes the primary contrast and the link AUROCs by at most 0.03, and also removing every item flagged by the sandbox audit for either model changes them by at most 0.09.
- L9. The task sandbox was a temporary directory, not a filesystem jail; an audit of every tool call found no hidden-test input reaching an agent from a file, but the audit matches only test arguments of 15 or more characters, and the control-arm sessions were not audited.
- L10. One sample per item and model at default sampling settings, so run-to-run variation of the agents is not measured; re-executing all 1,200 scored solutions reproduced every recorded test result, so test execution itself was stable.
- L11. Only the six tests of the confirmatory family are corrected for multiplicity (Holm); all other intervals, including every subset and exploratory cell, are uncorrected and descriptive.
- L12. ECE with 10 equal-width bins is biased upward in finite samples and, with confidences concentrated in two bins, is close to the overconfidence gap; we use the Brier score for model comparisons.
- L13. Sonnet's initial confidences take 16 distinct values with 253 of 300 at 0.90 or above, so its link slope is in effect a two-band contrast; AUROC is the main statistic and slopes are not compared across models.
- L14. The agents ran with the experimenter's two Claude Code PreToolUse guard hooks active (they block publishing and approval-gated commands and add nothing to the context unless a call is blocked); blocked calls were not counted.
- L15. The degenerate-input trap group was named in the preregistration, but its membership rule (a regex over the trap rationales) was written after the data were seen; most trap fixes came from this group (8/13 vs 2/14 Haiku, 11/14 vs 2/15 Sonnet).
- L16. The Haiku-Sonnet comparison of defense is underpowered (paired FTR_3 difference 0.04 [-0.12, 0.20]; on the 51 items both models got wrong, 15 vs 19 fixed, exact McNemar p = 0.45), and we do not claim the models differ in how they defend their work.
- L17. Our novelty check read the two closest concurrent papers only in part (about 28% and 42% verbatim), so the statement that they do not test the confidence-defense link is limited to the parts read.

## Published transcripts

`out/*.jsonl` in the repository are copies made by `scrub_transcripts.py`: local absolute paths inside text fields
(the sandbox temp dir and two paths an agent named in a reply) are replaced by `<sandbox>` / `<local path>`; every
field used by a metric is identical to the raw file, and `recount.py` reproduces the tables from these copies.
