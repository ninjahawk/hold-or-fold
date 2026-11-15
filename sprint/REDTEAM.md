# REDTEAM: three independent reviews of the frozen results, and the response to every issue

Run Sat 2026-11-14 09:08 ET. Each reviewer was a fresh `claude -p --model claude-opus-5-5` session in its own copy of
`sprint/PREREG.md`, `NOVELTY.md`, `RESULTS.md`, `out/results.json`, `out/results_tables.md`, `fig/*.png`,
`sprint/*.py` and `prebuild/harness/` (the state of commit `1537c6b`), with `--allowedTools Read,Grep,Glob`,
`--add-dir <that copy>` and `--strict-mcp-config`. They got only their role prompt (below), no opinion and no
expected result. API-equivalent cost reported by the CLI: AC USD 1.01, judge USD 0.78, statistician USD 1.07.

Prompts (verbatim, after a common header naming the files):
- AREA CHAIR: "Would you accept this as a workshop paper? List every methodological flaw, confound and overclaim, most serious first. For each: what evidence or analysis would resolve it."
- SPRINT JUDGE: the Track 1 text and the Judging rubric pasted verbatim from the sprint page notes (the page gives anchors 4-5 for Impact, 3-5 for Execution, 2 and 5 for Presentation; all given anchors were pasted), then "Score 1-5 on each with one line why; then the 3 changes that would raise the score most; flag anything a judge could read as made-up or unsupported (that disqualifies)."
- STATISTICIAN: "Check every estimate, CI and test: bootstrap unit (item-level?), paired Haiku-vs-Sonnet comparisons, multiple comparisons, small-n cells (trap subsets, originally-wrong n), the calibration-defense link slope/AUROC, deviations from the preregistration. List errors and anything reported more strongly than the data allow."

## Review 1: AREA CHAIR (ML venue) (verbatim)

### Area chair review: calibration and claim-defense of coding agents under escalating rebuttals

**Recommendation: borderline. I would accept it as a workshop paper only if the claims are rewritten (major revision).**

The process is well above typical sprint standard:
- a frozen preregistration with a recorded freeze commit;
- the switch rule and cost rule were followed and logged;
- no items were dropped (0 drops, 0 confidence-parse failures);
- an independent recount found 0 mismatches;
- deviations are listed honestly;
- Wilson intervals are added where the bootstrap collapses;
- a sandbox access audit was done.

The problem is interpretation. Several of the six candidate headlines (`RESULTS.md` lines 422–427) read the designed trap set and the forced-edit design as if they were properties of the models. And the paper's own preregistered decision rule is never applied to the key analysis.

---

##### AC1. The preregistered decision rule for the key analysis is never applied, and its result is softened in the write-up
- **The rule:** `PREREG.md` ("What would change the conclusion") says that if confidence predicts holding on correct items but predicts *less* fixing on wrong items, that means stubbornness rather than discernment.
- **What the data show:**
  - For Haiku on non-trap items, the fixed-when-wrong AUROC is **0.28 [0.12, 0.48]** (`RESULTS.md` l.83). The CI excludes 0.5, and the held-when-correct AUROC is 0.82 [0.70, 0.93].
  - On all items, Haiku's fixed-when-wrong AUROC is 0.39 [0.24, 0.55]. The link figure shows the same monotone pattern: 50% fixed below 80 confidence, 39% at 80–89, 28% at 90+.
  - This is the preregistered stubbornness signature for Haiku.
- **How the write-up reports it:** headline 2 says only that confidence "does not predict which wrong solutions get fixed", which hides the direction. RESULTS never states which preregistered outcome occurred, per model.
- **Resolution:** add a section that applies each "what would change the conclusion" rule, per model, with its CI. State plainly: Haiku matches the stubbornness pattern on non-trap items; Sonnet is inconclusive (0.47 [0.19, 0.76], n=26, 9 fixed).

##### AC2. Item difficulty confounds the calibration-defense link
- Confidence, original correctness and robustness to editing probably share one cause: how easy the item is.
  - An easy item draws high confidence.
  - A correct solution to an easy item is unlikely to break when edited.
  - A wrong solution to an easy item may be easy to repair.
- So a held-when-correct AUROC of 0.78–0.88 does not show that the *model's confidence* carries information about defense. It may only show that easy items are easy.
- The 51 items both models got wrong (`RESULTS.md` l.128) shows how strongly item effects dominate: Haiku had 58 wrong, Sonnet 55, and 51 of them overlap.
- **Resolution:**
  - Add an item-difficulty covariate to the logistic models, e.g. the other model's correctness, `hidden_n_passed`/`hidden_n`, benchmark source, or canonical solution length.
  - Better: rerun a subset with k≥5 samples per item and test the link *within* items (does a sample with higher confidence hold better than another sample of the same item?).
  - At minimum, stratify by MBPP+ vs HumanEval+.

##### AC3. The trap set is built so the model's natural answer fails, yet trap results are presented as model overconfidence (headlines 3 and 4)
- **How traps are scored:** on a trap, the canonical solution fails "one plausible alternate-reading test". A model that implements the canonical, presumably natural reading is therefore scored *wrong*.
- **Headline 3 overclaims:** confidence of 89%/92% against 33%/28% accuracy (ECE 0.57/0.65) measures how ambiguous the authors' specs are, not overconfidence. Nothing in the prompt tells the model the alternate reading is intended.
- **Headline 4 depends on the traps:**
  - On non-trap items, overconfidence is −0.01 [−0.05, 0.03] for Haiku and 0.02 [−0.01, 0.06] for Sonnet. Neither is distinguishable from zero.
  - The paired overconfidence gap of 0.04 [0.02, 0.06] is computed on all items. It is mainly Sonnet reporting higher numbers on a confidence scale compressed near the top: 253 of 300 Sonnet confidences fall in the 0.9–1.0 bin (`results.json`, reliability).
- **The traps cannot be validated:** they were "written for this study" (l.409), with no account of who wrote them, how, or whether they were validated. `prebuild/data/traps.jsonl` is not in the submission.
- **Resolution:**
  - Report calibration on non-trap items as the primary result.
  - Rerun the paired comparison on non-trap items only.
  - Get independent human ratings of whether each trap's prompt actually supports the alternate reading, and whether a careful engineer would choose it. Release `traps.jsonl` with those ratings.
  - Rewrite headlines 3 and 4 accordingly.

##### AC4. The "all items" metrics depend on a mixture the authors chose
- Traps are 13% of items but about half of the originally-wrong items: 27 of 58 for Haiku, 29 of 55 for Sonnet.
- So FTR, the primary contrast, and every fixed-when-wrong link on "all items" are roughly half driven by an artificial subpopulation whose share was set by design (40 of 300).
- Brier, ECE and FTR on "all items" are therefore not estimates for any natural population.
- **Resolution:** make non-trap items primary for every metric, report traps as a separate stress test, and drop pooled "all items" figures from the headlines.

##### AC5. FTW measures breakage under a forced edit, not capitulation, so headline 1 understates how often models fold
- **The numbers:**

  | Correct items at rebuttal 3 | Haiku | Sonnet |
  |---|---|---|
  | Code changed | 42% | 51% |
  | Ended up failing hidden tests | 8% | 7% |

- So the models gave in on code about half the time. Most of those edits happened not to break anything, probably defensive edge-case code or cosmetic changes. The sha comparison (`runner.py` `_norm`) counts comment-only changes as changes.
- Headline 1, "broke only 8% and 7%", reads as robustness. It is mostly the harmlessness of the edits.
- The two models also differ sharply in stated confidence: on correct items, Haiku's confidence drops by 0.32 at turn 3 and Sonnet's by 0.05. That is a belief-level capitulation difference the headlines do not mention.
- **Resolution:**
  - Report a code-capitulation rate: correct items with a semantic change, judged by AST diff or behavior on extra inputs.
  - Report a stated-belief capitulation rate: the model says its code was wrong, or confidence drops by at least 20 points.
  - Present breakage as a third, separate quantity.

##### AC6. The primary contrast FTR₃ − FTW₃ mixes ability with discernment and has no baseline
- **Ability limits FTR:** the model can only fix a solution if it can find the bug without being told what the failing test is. FTR is therefore capped by coding ability, not just by resistance to sycophancy. A model that never edits scores 0, and so does an ideal model that cannot locate bugs.
- **FTR and FTW have different denominators:** FTR is computed on the wrong items, which are harder and include the traps, and FTW on the correct items. Their difference is not a clean discernment measure.
- **Missing baselines:**
  1. A fresh re-solve in a new session for the originally-wrong items. Is 36–40% better than simply sampling again?
  2. An informative-feedback upper bound: show the actual failing hidden test.
- **The traps show the problem:** FTR₃ is 0.62 and 0.79 on degenerate-input traps but 0.14 and 0.13 on the other traps (l.57–58 and l.97–98). "Fixing" is largely generic defensive handling of empty input, not diagnosis.
- **Resolution:** add both baselines, and report FTR on non-trap and non-degenerate items with the degenerate share shown explicitly.

##### AC7. The control arm is too small for the causal claim in headline 6
- **The data:** 60 items per model, 11 originally wrong. Fixed: 0/11 for Haiku and 1/11 for Sonnet, with Wilson upper bounds of 0.26 and 0.38.
- **My Fisher's exact tests against the main arm's FTR₃:**

  | Comparison | Main arm | Control arm | p |
  |---|---|---|---|
  | Haiku, all items | 21/58 | 0/11 | 0.015 |
  | Sonnet, all items | 22/55 | 1/11 | 0.08 |
  | Haiku, non-trap | 11/31 | 0/7 | 0.08 |
  | Sonnet, non-trap | 9/26 | 1/7 | 0.40 |

- The arms are also separate unpaired samples: fresh sessions with different initial solutions. The comparison was not preregistered as a test.
- The control rules out repetition alone. It does not separate the "reviewer says" wording from the "hidden tests fail. Fix it." wording, or from the imperative "Fix it". Strength and position are still confounded (acknowledged at l.410).
- **Resolution:**
  - Soften headline 6 to: "consistent with; significant for Haiku only."
  - Use a counterbalanced design in which each rebuttal type appears as the *first* challenge in its own arm.
  - Include a "Fix it" instruction with no claim of failure, to separate "being told to edit" from "being told it fails".

##### AC8. Non-trap "wrong" items have not been checked for benchmark artifacts
- At 88–90% accuracy on MBPP+/HumanEval+, the remaining failures are often known MBPP+ test quirks: type strictness, float handling, or underspecified prompts. The 51-of-55 overlap between models supports this.
- If many "originally wrong" non-trap items are unfixable without the hidden test, FTR and fixed-when-wrong links measure the benchmark, not the model.
- **Resolution:**
  - Have humans audit the 31 and 26 non-trap wrong items, classifying each as a genuine bug or a spec/test artifact.
  - Report the `hidden_n_passed` distribution to separate near-misses from wholesale failures.
  - Redo FTR and the link on genuine bugs only.

##### AC9. Contamination and the sandbox audit: leak detection is weak and two of Haiku's items read the data file
- **Data-file reads:** Haiku has `data_read` = 2 (`HumanEval/43`, `mbpp/580`). These are calls that read a file naming the item data. "No hidden-test content reached any agent from a file" (l.392) depends on `file_leak`, which only matches hidden-test argument strings of at least 15 characters (`audit_access.py` `hidden_strings`). Many MBPP hidden inputs are shorter, so sensitivity is low.
- **Memorized tests:** "recall" covers 44 Haiku items and 31 Sonnet items where the agent typed two or more hidden-test inputs itself, meaning memorized public benchmark tests. Memorization raises both confidence and correctness, which inflates calibration and the held-correct link, and it is never controlled.
- **Unaudited arm:** the robustness-arm sessions were not audited.
- **Resolution:**
  - Quote the actual tool calls for the two `data_read` items.
  - Lower the leak threshold, or match test *outputs* as well as inputs.
  - Rerun the link and calibration with recall items excluded, and with recall as a covariate.
  - Audit the robustness arm.
  - Ideally, run in a filesystem jail (e.g. bubblewrap or a container).

##### AC10. The link estimates are fragile: few events, compressed confidence, and bootstrap draws silently discarded
- **Few events:** held-when-correct has only 19 negatives for Haiku and 16 for Sonnet.
- **Implausible slopes:** Sonnet's slopes of 2.10–2.35 log-odds per 0.1 confidence, with upper CIs of 4–5, point to near-separation on a confidence range packed between 0.85 and 0.95.
- **Empty or tiny bins:** in the link figure, Sonnet's "<80" band has n=1 (held) and n=2 (fixed).
- **Discarded draws:** `analyze.boot` drops not-estimable resamples. For Sonnet non-trap, 116 of 2000 held-correct slope draws and 116 of 2000 fixed-wrong slope draws were discarded (`results.json` `link_nontrap_ci`; Haiku lost 27 fixed-wrong draws). The CIs are therefore conditional on estimability, and the table does not say so.
- **Resolution:**
  - Use Firth-penalized logistic regression or a Bayesian logistic model with a weak prior.
  - Report the number of valid draws.
  - Lead with AUROC, since the preregistration already allows that.
  - Note that tied confidences ("90", "95") make AUROC coarse, and report the number of distinct confidence values.

##### AC11. The "paired" comparison of FTR₃ is not paired
- FTR conditions on each model's *own* wrong set. The paired bootstrap resamples items, but the two models' conditional rates have different denominators.
- **Resolution:** compute the paired FTR and link difference on the 51 both-wrong items, and the paired FTW difference on the items both models got right.

##### AC12. One sample per item at default temperature, with execution noise not ruled out
- With one sample per item, model behavior cannot be separated from sampling noise. This matters most for the item-level link (see AC2).
- A flip is also a binary all-tests-pass flip under a 5-second per-test timeout, with 4 shards running in parallel. Timeout-induced flips (`exec_error`) were not checked.
- **Resolution:**
  - Re-execute every final solution twice in isolation and report how many flips are unstable.
  - Break down flips by `exec_error`.
  - Report the partial-pass change (Δ`hidden_n_passed`).

##### AC13. Many comparisons, with headlines picked afterwards
- RESULTS reports about 5 subsets × 15 metrics × 2 models, plus link tables, a sensitivity analysis and a control arm, with no correction for multiple comparisons.
- The "candidate headline sentences" were selected after the data were seen.
- The confidence bands in the link figure were "fixed before Sonnet data were seen", which means after the Haiku data were seen.
- **Resolution:** limit headlines to the preregistered primary and key analyses, run on the preregistered subset, and label everything else exploratory in the main text, not just in the deviations list.

##### AC14. The scope is too narrow for the "coding agent" framing
- Two models from one family, run through `claude -p`, on single-function MBPP/HumanEval tasks.
- These are not agentic, multi-file or SWE-style tasks, which is exactly what the closest prior work, Thinking-in-Bets on SWE-Pushback-Hidden, uses.
- The planned 7B arm was not run.
- **Resolution:** frame the work as "function-level code generation with tool access". Add a small SWE-style slice, or a non-Anthropic model, if the general claim is kept.

##### AC15. The novelty check is incomplete
- Both concurrent papers were only partly read: about 28% and 42% verbatim, with the "does not test the link" claim qualified as "in the parts read".
- The earlier literature on challenge-induced answer flipping and its relation to model confidence is not cited, including:
  - Laban et al. 2023, "Are you sure?" / FlipFlop;
  - Wang et al. 2023, "Can ChatGPT defend its belief in truth?";
  - Sharma et al. 2023 on sycophancy;
  - Xie et al. 2023, "Ask Again, Then Fail".
- That literature directly bears on the claimed new quantity.
- **Resolution:** read both concurrent papers in full and cite the earlier work. Narrow the novelty claim to "the link measured with execution-based ground truth on coding tasks under a fixed ladder".

##### AC16. Smaller presentation and harness issues
- **(a) Unweighted reliability bins:** the reliability diagram (`fig/headline.png`) gives single-item bins the same weight as large ones. Haiku's spikes at 0.35 (n=1), 0.55 (n=1) and 0.25 (n=1) dominate the plot visually. Show n per bin and drop bins with n<5.
- **(b) Trap relabelling in the figure (D7):** relabelling traps as non-trap for the trap figure is harmless but should be fixed in the scorer, not worked around.
- **(c) User hooks in the experiment harness:** the user's personal Claude Code hooks are re-applied inside the experiment (`backends.user_hooks_settings`). Hooks can inject context or block calls, which threatens reproducibility. List the hooks that were active, or run with none.
- **(d) Edits in the confidence turn:** a model that edits its code in the confidence turn makes y₀ refer to post-confidence code. Report how often `solution_sha` changed between the solve turn and the confidence turn.
- **(e) Transcripts:** the scrubbed transcripts are said to be in the repo but were not provided to reviewers. Include them so the recount can be checked.

---

**What would get it to accept:**
- Lead with non-trap items.
- Report the preregistered outcome for each model (Haiku's stubbornness signature, AC1).
- Add a difficulty control or within-item replicates to the link (AC2).
- Reframe the traps as an ambiguity stress test (AC3).
- Split FTW into code, belief and breakage measures (AC5).
- Add a re-sample baseline for FTR (AC6).
- Soften headline 6 to the Fisher result (AC7).

None of this needs new infrastructure. Apart from AC2's replicate runs and AC6's baselines, everything is reanalysis of transcripts the authors already have.

## Review 2: SPRINT JUDGE (Apart AI x Epistemics, Track 1) (verbatim)

I'd score it **Impact 3, Execution 4, Presentation 2**. The method is strong for a sprint, but there is no actual report and some headline wording claims more than the data shows. I found no sign of made-up numbers. Every figure I checked recomputes from the counts and matches `out/results.json`.

#### Scores

| Dimension | Score | Why |
|---|---|---|
| Impact & Innovation | **3** | It fits Track 1's "gap between what a model implies and what it will defend" well, and it tests this against hidden-test results rather than a grader's opinion. But `NOVELTY.md` admits concurrent papers already measure each half, the one new quantity (does confidence predict holding or fixing) mostly comes out null, only two models from one family were run, and the 7B arm was dropped. |
| Execution Quality | **4** | Clearly above a typical sprint: frozen preregistration with a stop/switch rule (checked: 24 of the first 100 wrong, 13 non-trap), a list of deviations, paired bootstrap, an independent recount with 0 mismatches, a sandbox-access audit with a rerun excluding flagged items, and a neutral-only control arm. It falls short of 5 because there is no ceiling for how many wrong solutions could be fixed (J7), the trap items are ambiguous by design (J8), the control arm is small (J9), and the preregistered conclusion test is never answered (J5). |
| Presentation & Clarity | **2** | This is the rubric's 2 almost word for word: "key information buried, missing, or diluted by excessive length." There is no abstract, motivation, discussion or conclusion. `RESULTS.md` is 427 lines of copied tables, compute-plan meter logs and six "candidate headline sentences." |

#### The 3 changes that would raise the score most

1. **Write the actual report (Presentation 2 → 4).** It needs about 2 pages: the question, the method in one paragraph with Fig. `headline.png` and `link.png`, 3–4 findings, and limitations. Move everything else to an appendix:
   - the full tables;
   - the sensitivity tables, which repeat lines 178–268 almost unchanged;
   - the meter log with "job #2158" and the five-hour plan window (lines 21–41), which has nothing to do with the research.

   Turn the "candidate headline sentences" into claims the authors actually make.
2. **State the preregistered verdict and lead with the most interesting result (Impact +1).** PREREG ("What would change the conclusion") defines a stubbornness pattern: confidence positively linked to holding correct code and negatively linked to fixing wrong code. Haiku's non-trap results fit that pattern:
   - held-when-correct: AUROC 0.82 [0.70, 0.93];
   - fixed-when-wrong: AUROC **0.28 [0.12, 0.48]**, whose interval excludes 0.5.

   So for Haiku, high confidence means holding regardless of truth. Sonnet does not show it (0.47). Say this outright, with a caveat about how many comparisons were run. Also add the most basic calibration number: AUROC of initial confidence for initial correctness.
3. **Add a fixability ceiling and handle the traps and recall cases (Execution 4 → 5).** "Fixed only 36%/40%" means little without knowing how many of those wrong solutions could be fixed at all without seeing the hidden tests. Options: a pass@k re-solve, or a turn that names the failing test. Report trap results only with clear-spec and ambiguous-spec items kept apart. Rerun the link analysis without the 44 Haiku and 31 Sonnet items where the agent typed hidden-test inputs itself (likely memorised public tests).

#### Issues

- **J1 (Presentation)** No report text at all. `RESULTS.md` line 1 calls itself "plain facts." The judge has to work out the findings from the tables.
- **J2 (Presentation)** About a quarter of `RESULTS.md` is noise: plan meter readings, job IDs, the five-hour window, `can_rc` checks (lines 14–41). The sensitivity tables (lines 178–268) repeat the main tables and could be one sentence: "all metrics within CI; see appendix."
- **J3 (Presentation)** The reliability diagram (`fig/headline.png`, panel a) plots bins holding a single item as full points. Haiku's spike to 1.0 at 0.35 and drop to 0.0 at 0.25 and 0.55 are each n=1 (`results.json` reliability). Sonnet has 253 of 300 items in the 0.9–1.0 bin, so the plot is mostly noise. Show counts per bin or hide small bins. The n labels in `fig/link.png` also overlap ("n=160/n=210", "n=10/n=2").
- **J4 (Impact)** The literature check covers only two concurrent arXiv papers. It leaves out the obvious prior work on challenging models with "are you sure?" and on stated confidence, e.g. Laban et al. 2023 (FlipFlop, which matches the track's own "flip-flopping" wording), Sharma et al. 2023 on sycophancy, Kadavath et al. 2022, Xiong et al. 2023. Without these, the novelty claim is weaker.
- **J5 (Execution)** PREREG sets three outcome scenarios ("null on capitulation" / "capitulation" / "stubbornness"). `RESULTS.md` never says which one happened. The answer is roughly: little capitulation (FTW_3 = 0.07–0.08), some fixing (FTR_3 = 0.36–0.40), and stubbornness only for non-trap Haiku.
- **J6 (Execution)** Initial confidence barely varies, which limits what the link analysis can show. For Sonnet, 253 of 300 items fall in the 0.9–1.0 bin and only 1 correct item is below 80. Its held slope of 2.10 [1.10, 4.07] rests on 16 failures, mostly in the 80–89 band (26/34 held). The report should say this.
- **J7 (Execution)** There is no ceiling for FTR. The agent never sees the hidden tests, so a low FTR may mean the bug can't be found from the spec, not that the model updates poorly. Headline 5 ("64%/60% still failed") reads as an epistemic failure without that baseline.
- **J8 (Execution)** The traps are built so that "the canonical solution fails one plausible alternate-reading test" (PREREG, Data). By construction the spec is ambiguous, so high confidence there is not plainly miscalibration, and a "fix" means guessing the other reading. 17 of 40 traps are about empty or degenerate inputs, and their FTR (0.62 Haiku / 0.79 Sonnet) differs sharply from the rest (0.14 / 0.13). Pooled trap numbers (headline 3: ECE 0.57/0.65) mix these two kinds.
- **J9 (Execution)** The control arm has only 11 wrong items per model, drawn from a different subset (seed-1 sample of 60). Headline 6 makes a causal claim ("the fixes appeared when the agent was told its work fails") from 0/11 and 1/11. These 60 items were also run in the main arm, so a within-item comparison is possible and should be shown, with an exact test.
- **J10 (Execution)** The sandbox was not isolated: the agent's Bash tool could read the rest of the machine, including in principle the data directory. The audit found 0 file leaks, which is good. But the robustness-arm sessions were not audited (D5), and the 44/31 "recall" items stay in every analysis (see change 3).
- **J11 (Execution)** About 18 link results are reported (2 models × 2 subsets × 3 outcomes, plus the trap split) with no correction for multiple comparisons. Under such a correction, the Haiku inverse effect in J5 may not survive.
- **J12 (Execution)** Haiku's confidence on correct items drops 0.32 at turn 3; Sonnet's drops only 0.05, even though Sonnet changes 51% of correct solutions. That is close to the track's "retreating quietly under pushback" / implied-vs-defended gap, and it is not analysed.

#### Flags a judge could read as made-up or unsupported

I don't see grounds to disqualify. I recomputed these and they hold:
- FTW_3 19/242 = 0.079 and FTR_3 21/58 = 0.362 (Haiku); FTR_3 22/55 = 0.40 (Sonnet).
- The band counts in the link table add up to the link-table n's (223/242, 21/58, 229/245, 22/55).
- Trap confidence and accuracy (0.891 / 0.325) match `results.json`.
- `results_tables.md` matches the tables quoted in `RESULTS.md`.

These points still need fixing so a judge doesn't mark them down:

- **F1** `RESULTS.md` and PREREG cite files that are not in the submission:
  - `runset.json`, `out/link_bands.json`, `out/recount.txt`, `logs/sonnet_blocks.log`, `sprint/tests/test_linux.py`, `harness_patches/` and `fig/link.pdf`;
  - `out/*.jsonl`, which line 415 says are "in the repository";
  - the freeze commit `8a07d53`, with no repo provided.

  The recount ("mismatches: 0") and the preregistration timing can't be checked. Include these files or link a public repo.
- **F2** The two arXiv references in `NOVELTY.md` (2610.34654, 2611.10063) have no authors or URLs. The file also admits only 28% and 42% of each paper was read word for word, the rest "via a summary." Its claim that Thinking-in-Bets "does not test whether initial confidence predicts…" therefore rests partly on parts nobody read. Add links and either finish reading or soften the claim.
- **F3** The timing around the freeze is unclear. Line 41 says the meter was read "at job start, Fri 22:00 ET," and the freeze was "~22:15 ET." A judge could take that as runs starting before the freeze. State when the first model call happened.
- **F4** Headline 2 says confidence does "not" predict which wrong solutions get fixed (AUROC 0.39 [0.24, 0.55]). That understates the significant inverse effect in non-trap Haiku (0.28 [0.12, 0.48]).
- **F5** Headlines 1 and 5 call fixing "only" 36–40% a failure without a ceiling (J7). Headline 6 makes a causal claim from n=11 (J9). These overclaim; they are not invented numbers.

## Review 3: STATISTICIAN (verbatim)

### Statistical review: calibration and rebuttal-defense sprint (Haiku 5.5 vs Sonnet 5.5)

**Bottom line.** The point estimates are computed correctly. `recount.py` reproduces them, the bootstrap resamples whole items, and the paired comparison resamples item pairs. Six things are wrong or claimed more strongly than the data allow:

- The qualitative wording of the headline sentences is hard-coded.
- One "no effect" claim hides a significant negative result.
- The main-arm vs control-arm comparison is untested, unpaired and not significant for Sonnet.
- The slope CIs drop the bootstrap draws that failed.
- The pooled "all" estimates mix in traps at a ratio the authors chose.
- Several small-n cells are reported with zero-width percentile intervals.

I could not recompute CIs because the raw transcripts are not included. The checks below use `out/results.json`, the code, and Fisher exact tests I computed from the reported counts.

#### Errors and overstatements, most serious first

**S1. The conclusion text of the headline sentences is fixed in code, not driven by the data.** In `make_results.py:54-56` the words "predicts which correct solutions survive … but not which wrong solutions get fixed" are a literal string; only the numbers are filled in. The same is true of headline 6 (`make_results.py:80-81`): "the fixes in the main arm appeared when the agent was told its work fails, not under repeated neutral checking." These sentences would print unchanged whatever the CIs showed. Each claim needs to be re-derived from the data (see S2, S3).

**S2. Headline 2 ("does not predict which wrong solutions get fixed") hides a significant inverse effect for Haiku, and it never applies the preregistered decision rule.**
- For non-trap Haiku, the fixed_wrong AUROC is **0.28 [0.12, 0.48]** (RESULTS.md:83). The interval excludes 0.5, so higher initial confidence significantly predicts *not* fixing wrong work.
- At the same time, held_correct is 0.82 [0.70, 0.93].
- That is the PREREG's "stubbornness" pattern: "slopes positive on correct items and negative on wrong items: high confidence means holding regardless of truth". The confidence bands agree: Haiku fixed 5/10, 9/23 and 7/25 across the three bands, a monotone decline.
- The headline quotes only the "all items" AUROC (0.39 [0.24, 0.55]) and calls it "not predicting".
- For Sonnet, 0.57 [0.42, 0.74] (non-trap 0.47 [0.19, 0.76]) is absence of evidence, not evidence of no link. The interval allows anything from a moderate inverse to a moderate positive relation.
- RESULTS never states which of the three PREREG "what would change the conclusion" outcomes occurred.

**S3. Headline 6 (control arm) makes a causal claim from an untested, unpaired comparison that is not significant for Sonnet.**
- Main-arm FTR_3 vs control-arm FTR_3, Fisher exact (my calculation):
  - Haiku 21/58 vs 0/11: p = 0.015.
  - Sonnet 22/55 vs 1/11: p = 0.08.
  - Non-trap only: Haiku 11/31 vs 0/7, p = 0.08; Sonnet 9/26 vs 1/7, p = 0.40.
- The two arms are separate runs with separate solves, so the "originally wrong" sets differ: 11 control items vs 55–58 main items, drawn from a seed-1 subset.
- All 60 control items are also in the main run set. A within-item comparison was possible but was not done.
- The control also removes the *content* of rebuttal 3 ("the hidden tests fail"), which tells a wrong solution something true. So it cannot separate pressure from information.
- Suggested wording: "consistent with". Report the test, or the within-item paired analysis.

**S4. The slope CIs are computed only on draws where the fit converged, which biases them.**
- `boot()` silently drops NaN draws (`analyze.py:45-46`).
- `logit_slope` returns NaN when an outcome class has fewer than 5 items, when the fit does not converge in 50 iterations, or when |b| ≥ 1000 (`analyze.py:54, 69-71`). Those are exactly the near-separation draws with the most extreme slopes.
- Valid draws per CI (from the third element of each CI in `results.json`):

| Cell | Valid draws | Dropped |
|---|---|---|
| Sonnet non-trap held_correct | 1942/2000 | 58 |
| Sonnet non-trap fixed_wrong | 1884/2000 | 116 |
| Haiku non-trap fixed_wrong | 1973/2000 | 27 |
| Haiku non-trap held_correct | 1997/2000 | 3 |

- Dropping these draws pulls in the outer tails. The Sonnet held slope (2.35 [1.33, 5.07]) and the fixed_wrong slopes are reported as narrower than they are.
- The number of valid draws is not shown anywhere in RESULTS.md.
- **Fix:** use Firth or penalized logistic regression, or report the dropped fraction and treat a dropped draw as ±∞.

**S5. The preregistered "not estimable" rule is broken in the robustness tables.**
- PREREG says a slope with fewer than 5 items in an outcome class is reported as not estimable, with only the AUROC given.
- The Sonnet robustness table still prints "nan [-4.65, 1.21]" with n_pos = 1 (RESULTS.md:342), and "nan [-2.89, 2.38]" (RESULTS.md:350).
- Those intervals come only from resamples that happened to duplicate the single positive item 5 or more times. They are meaningless.
- The AUROC with one positive (0.30 [0.06, 0.58]) is also nearly uninformative and should be flagged.

**S6. The Sonnet held_correct slope (2.10 per 0.1, odds ratio about 8 per 10 points) rests on a narrow, lumpy confidence range.**
- Sonnet confidences: 253 of 300 in the 0.9 bin, 44 in the 0.8 bin, 3 below 0.8. Among originally-correct items, only 1 is below 80.
- The slope is in effect a two-group contrast: 26/34 held in the 80–89 band vs 202/210 at ≥90.
- The band rates are not monotone (the single <80 item held: 1/1). The linear-logit form is not checked.
- Comparing Sonnet's 2.10 with Haiku's 0.81 mixes different confidence spreads: Haiku's c0 has a much wider range.
- **Fix:** present AUROC as the primary statistic, as PREREG already suggests ("robust to separation"). Do not compare slopes across models.

**S7. The pooled "all" estimates depend on a trap share that the authors chose.**
- Traps are 40/300 = 13% of items but 47–53% of the originally-wrong items (Haiku 27/58, Sonnet 29/55).
- Headline 1's FTR_3 (0.36, 0.40) and contrast (0.28, 0.33) therefore describe an arbitrary mixture.
- Haiku's "all" overconfidence of 0.07 [0.02, 0.11] comes entirely from the traps: non-trap it is −0.01 [−0.05, 0.03].
- PREREG made "all" the primary, so this is not a deviation. It is still an interpretive error to present "all" without its non-trap counterpart.
- Non-trap FTR_3 is 11/31 = 0.35 and 9/26 = 0.35.
- The CIs on "all" also come from an unstratified bootstrap (`analyze.py:40`). Each resample's trap count varies even though the design fixes it at 40. A stratified bootstrap would match the design.

**S8. Headline 1 says "n = 300 items each", but the rates it quotes have different denominators.**
- FTW_3 is out of 242 and 245 correct items; FTR_3 is out of 58 and 55 wrong items.
- The phrase "broke only 8% … but fixed only 36%" does not mention that 42% and 51% of correct solutions had their code changed at turn 3. FTW_3 is a combination of how often the model changes code and how often a change breaks it.

**S9. Headline 4 (Sonnet more overconfident on the same items) uses only the pooled set; PREREG asked for a trap/non-trap split.**
- Paired comparisons appear only for "all" (`analyze.py:236`). PREREG says the secondary metrics are "all split trap / non-trap".
- On non-trap items the unpaired point estimates already shrink the claim:
  - Accuracy 0.90 vs 0.88 (difference about +0.02).
  - Overconfidence 0.02 vs −0.01 (difference about +0.03).
  - Part of the pooled "not more accurate" comes from Sonnet's lower trap accuracy (0.28 vs 0.33, n = 40).
- "Without being more accurate" (0.01 [−0.01, 0.03]) is absence of evidence. The interval allows Sonnet to be up to 3 points more accurate.
- The three numbers are one finding, not three: the overconfidence difference equals the confidence difference minus the accuracy difference.

**S10. ECE percentile CIs and paired ECE differences are unreliable.**
- ECE is biased upward in finite samples and is not a smooth statistic. Its lower bound can never support "calibrated".
- Signs of the problem:
  - Paired ECE difference 0.026 [−0.006, 0.044]: the point estimate sits near the upper end of its interval.
  - Sonnet non-trap ECE 0.02 [0.01, 0.06].
- With almost all confidences in two bins, the 10-bin ECE is in effect a 2-bin statistic. On traps it equals overconfidence exactly (RESULTS.md:56, 96).
- Brier, or a debiased ECE, would be the sounder basis for comparison.

**S11. Small-n cells are reported with percentile bootstrap intervals that are degenerate or anti-conservative.**
- Zero rates show as "0.00 [0.00, 0.00]" (FTW_1, FTR_1, every robustness-arm cell). That interval implies certainty.
- Haiku robustness FTR_3 − FTW_3 = "0.00 [0.00, 0.00]" on 0/11 and 0/49. The Wilson intervals give FTR up to 0.26 and FTW up to 0.07.
- Trap cells have 11–13 originally-correct items. Trap_without_degenerate has 7–9 correct and 13–15 wrong.
- Example: Haiku trap FTW_2 is 0.15 [0.00, 0.38] by bootstrap vs Wilson [0.04, 0.42] for 2/13.
- The Wilson tables exist but are labelled supplementary. For any cell with fewer than about 30 items, the Wilson interval (or exact, or a Newcombe interval for differences) should be the reported interval.

**S12. Multiple comparisons are not addressed, and exploratory "significant" cells invite misreading.**
- Count of intervals: 2 models × 5 subsets × 13 metrics, plus 2 × 2 × 3 link outcomes × 2 statistics, plus 8 paired metrics, all repeated three times (main, audit-clean, robustness). That is several hundred CIs with no adjustment and no designated family.
- The six headlines were chosen from this pool.
- Example: Sonnet audit-clean trap_without_degenerate contrast −0.44 [−0.86, −0.02] (RESULTS.md:227) is the kind of cell that will be quoted.
- **Fix:** name the confirmatory family (primary contrast × 2 models, the link AUROCs × 2 models) and label everything else exploratory, with adjusted or at least flagged intervals.

**S13. The degenerate-input trap split could be data-dependent, and it changes how trap FTR should be read.**
- The `DEGEN` regex (`analyze.py:19`) is not recorded as fixed before the data were seen. D6 only says the confidence *bands* were fixed before the Sonnet data.
- The split matters a great deal:
  - FTR_3 on degenerate traps is 8/13 vs 2/14 on the rest (Haiku, Fisher p = 0.018), and 11/14 vs 2/15 (Sonnet, p < 0.001).
  - So most trap "fixes" are one kind of edit (adding an empty-input guard), not evidence of discernment.
- The headlines treat trap FTR as a single number.

**S14. The paired FTR_3 and contrast comparisons are only partly paired.**
- FTR_3 conditions on each model's own wrong set (58 vs 55 items, 51 shared).
- The pair bootstrap is still valid for a difference of ratio estimators on a common item sample. But part of the difference reflects *which* items each model got wrong, not how it responds to a rebuttal.
- A within-pair analysis on the 51 items both models got wrong would isolate the defense behaviour.
- The CIs (ftr_3 0.038 [−0.118, 0.195]) show the comparison has little power anyway. It should not be read as "similar".

**S15. "Held when correct" is confounded with item difficulty.**
- Low c0 among correct items probably marks harder or ambiguous items. The model edits those more under pressure, and edits to them break more often.
- The link could reflect item difficulty rather than defense driven by confidence.
- Checks that would help:
  - Adjust for benchmark (MBPP+ vs HumanEval+) and for the other model's correctness on the same item.
  - Condition on whether the code was changed.

**S16. The sensitivity analysis uses a weak test of agreement and leaves out the larger contamination group.**
- "The sensitivity tables match the main tables within their CIs" (D5) is almost guaranteed: 282 of the 300 items are shared, so the intervals must overlap.
- The exploratory `recall` items were not removed: 44 Haiku items and 31 Sonnet items where the agent typed two or more hidden-test inputs itself. That is a bigger possible bias on accuracy and calibration than the 18 items that were removed.
- The robustness-arm sessions were not audited, as RESULTS states.

**S17. The independent recount checks only point estimates.**
- `recount.py` checks n, accuracy, confidence, Brier, ECE, FTW/FTR and the contrast, for all, non-trap and trap.
- It does not check any CI, the link slopes or AUROCs, the paired differences, or the trap_without_degenerate and degenerate-only subsets.
- "Mismatches: 0" should not be read as verifying the key analysis.

**S18. The figures show sample sizes and uncertainty inconsistently.**
- `fig/headline.png`, panel (a): reliability points from single-item bins (Haiku bins at 0.25, 0.35 and 0.55, each n = 1; Sonnet's bin at 0.35) are joined by lines with no n and no error bars. The large jagged swings come from 1–3 items.
- `fig/link.png`: the Sonnet <80 point (n = 1, 1/1 held) is drawn with the same weight as the other points and looks like a non-monotone pattern.
- **Fix:** drop or mark bins with n < 5, and show Wilson bars.

**S19. Smaller deviations and loose ends.**
- The switch rule was applied to "the first 100 Haiku items by completion time" under 4 parallel shards, while PREREG says "the first 100 Haiku items". This is harmless here: 24/13 is far above the thresholds.
- D4 (Sonnet paused for about 8 hours, then resumed) is disclosed properly. It splits Sonnet's items across time, and the split was decided by run order, not by result.
- `PREREG` says FTR/FTW/Brier etc. are "split trap / non-trap", but the paired block and the code-change and confidence-drop rates are shown only for "all" (RESULTS.md:60, 100).

#### What holds up
- Resampling items is the right bootstrap unit: one sample per item, and no trap shares its base item.
- The comparison is paired on a shared item set, and every item finished with no drops (300/300 per model), so there is no selection from attrition.
- The non-trap minimum (n_wrong ≥ 15) was met: 31 and 26.
- Within one model and one arm, the main point estimates are reproducible and computed as the preregistration defines them.

## Resolution of every issue

Commit `53b2a2d` = post-review analyses (`redteam_analysis.py` -> `out/redteam.json`, `out/redteam_tables.md`, sections A-L, reproduced in RESULTS.md), extended `recount.py`, `analyze.py --tables-only`, new figures, limitations L1-L17 (`RESULTS_notes.md`). The freeze commit that adds this file and the frozen RESULTS.md is listed in RESULTS.md's git history. "Sec. X" = section of `out/redteam_tables.md` / RESULTS.md "Exploratory analyses". "L#" = sentence in RESULTS.md "Limitations". No new model calls were made; no extra run passed the bar (no reviewer showed a confound that blocks the preregistered headline, and the requested baselines need a new arm).

| id | issue (short) | resolution | evidence / change / sentence |
|---|---|---|---|
| AC1 | Prereg decision rule never applied; Haiku non-trap fixed AUROC 0.28 softened to "does not predict" | FIXED | 53b2a2d: Sec. A applies all three PREREG rules per model and subset; RESULTS.md "Preregistered outcome". On the preregistered all-items test stubbornness is NOT established for Haiku (fixed slope -0.28 [-1.03, 0.20]); the non-trap split shows the AUROC pattern (0.28 [0.12, 0.48]), but with difficulty covariates the fixed slope goes to -0.02 [-0.91, 0.56] (Sec. H), so it is reported and not claimed. Headline 2 wording is now chosen from the CIs. |
| AC2 | Item difficulty confounds the link | FIXED (partly) + LIMITATION | Sec. H: held slope with covariates (other model's correctness, benchmark, trap) Haiku 0.88 [0.52, 1.77], Sonnet 2.12 [1.07, 4.89]; AUROC within MBPP+ 0.73/0.76 and HumanEval+ 0.94/0.91. Within-item replicates need new runs: L3. |
| AC3 | Traps scored by design; headlines 3-4 read ambiguity as overconfidence; traps not validated | FIXED + LIMITATION | Old headline 3 (trap ECE) and 4 (pooled overconfidence gap) dropped from the abstract sentences (D10). Non-trap paired comparison added (Sec. C: overconf +0.034 [0.016, 0.050], acc +0.019 [0.004, 0.038]). Traps are in the repo: `prebuild/data/traps.jsonl` (rationale + reference solution each), rejected candidates `prebuild/data/traps_rejected.txt` (41). No human rating: L2. |
| AC4 | "All items" mixture set by design | FIXED | RESULTS.md "How to read" states the mixture; every headline number has its non-trap value in the tables; stratified bootstrap of the primary (Sec. I): 0.28 [0.16, 0.42] / 0.33 [0.20, 0.46]. "All" stays primary because PREREG fixed it. |
| AC5 | FTW measures breakage under forced edits, not capitulation; belief retreat not reported | FIXED | Sec. E: on correct items at rebuttal 3, semantic (AST) change 41% / 51%, confidence drop >= 20 pts 79% / 5%, broke 8% / 7%. Headline 4 now reports the belief-vs-code retreat difference (prereg metrics conf_drop_correct_3, chg_correct_3). |
| AC6 | FTR has no ceiling/baseline; degenerate traps drive trap fixes | FIXED (analysis) + LIMITATION | "only" removed from headlines; near-miss share reported (Sec. F: median 97% of hidden tests passed on wrong items); trap kinds: 8/13 vs 2/14, 11/14 vs 2/15 (Sec. K); non-trap FTR_3 0.35 / 0.35 in tables. Re-solve and informative-feedback baselines need model calls: L1. |
| AC7 | Control arm too small for causal headline 6 | FIXED + LIMITATION | Sec. D: Fisher tests (Haiku 21/58 vs 0/11 p = 0.015; Sonnet 22/55 vs 1/11 p = 0.081; same 60 items Haiku 8/12 vs 0/11 p = 0.001). Headline 3 now rests on the main arm's own rebuttal-1 count (0/58, 0/55, preregistered FTR_1) with the control as support, no causal verb. L5, L6. |
| AC8 | Non-trap wrong items may be benchmark artifacts | FIXED (partly) + LIMITATION | Sec. F reports the partial-pass distribution (non-trap wrong median share passed 0.80 / 0.77). Hand audit not done: L7. |
| AC9 | Leak detection weak (15-char threshold); recall items uncontrolled; robust arm unaudited | FIXED (recall) + LIMITATION | Sec. G: without recall items, contrast and AUROCs move by <= 0.03; also without all audit-flagged items <= 0.09. The two `data_read` items are already excluded in the audit-clean tables. Threshold and unaudited control arm: L8, L9. |
| AC10 | Link fragile: few events, packed confidence, dropped bootstrap draws | FIXED | Sec. J + tables now show valid draws (e.g. Sonnet non-trap fixed 1884/2000); AUROC declared the statistic to quote; distinct c0 values reported (20 / 16, Sec. F). L13. Firth regression not added (AUROC is the prereg's separation-robust statistic). |
| AC11 | Paired FTR_3 is not really paired | FIXED | Sec. C within-pair: 51 both-wrong items, fixed 15 vs 19 (McNemar p = 0.45); 238 both-correct, broke 17 vs 13 (p = 0.45). L16. |
| AC12 | One sample; execution noise / timeouts unchecked | FIXED (execution) + LIMITATION | Sec. L: 1200 re-executions of the confidence-turn and rebuttal-3 solutions, 0 differ from the recorded result; exec_error count 0 on every turn (Sec. F). Agent sampling variation: L10. |
| AC13 | Many comparisons; headlines chosen after data | FIXED | Sec. B: confirmatory family of 6 prereg tests with Holm (contrasts p < 0.001; held AUROCs p < 0.001; fixed AUROCs p = 0.36). Headlines restricted to preregistered metrics; everything else labelled exploratory ("How to read"). L11. |
| AC14 | Scope narrower than "coding agents" | LIMITATION | L4. |
| AC15 | Novelty check partial; prior flip/sycophancy work not cited | LIMITATION | L17. For the prose writer: the reviewers name Laban et al. 2023 (FlipFlop), Wang et al. 2023 (defending beliefs in debate), Sharma et al. 2023 (sycophancy), Xie et al. 2023 (Ask Again, Then Fail), Kadavath et al. 2022, Xiong et al. 2023; verify each reference from the source before citing (made-up references disqualify). |
| AC16a | Unweighted single-item reliability bins | FIXED | 53b2a2d: `fig/calib_defense` (a) pools sparse low bins to n >= 10, marker area ~ n, Wilson bars. |
| AC16b | Trap relabelling workaround in plots.py (D7) | REBUTTED | Figure-only; the new figures (`figs_final.py`) read results.json and do not use it; the frozen scorer is preexisting code and is not edited (sprint rule). |
| AC16c | User hooks active in the harness | LIMITATION | L14 (two PreToolUse guard hooks; they add no context unless a call is blocked). |
| AC16d | Edits during the confidence turn | REBUTTED | Sec. F: 0/300 items per model had a solution change between turn 0 and turn 1. |
| AC16e | Transcripts not given to reviewers | REBUTTED | They are in the repo (`sprint/out/haiku.jsonl`, `sonnet.jsonl`, scrubbed copies; `recount.py` gives 0 mismatches on them). Reviewers were deliberately given a reduced bundle. |
| J1 | No report text | REBUTTED (scope) | RESULTS.md is the frozen numbers file; the report prose is written from it separately. Abstract sentences now at the top of RESULTS.md. |
| J2 | Meter logs, job ids and duplicated sensitivity tables clutter RESULTS | FIXED | Meter log and cost moved to "Appendix: compute cost"; the sensitivity tables are kept but after the main and exploratory sections. |
| J3 | Reliability bins of n=1; overlapping n labels in link.png | FIXED | `fig/calib_defense.*` (pooled bins); `fig/link.*` labels offset per model, bands with n < 5 hollow (`fig_link.py`). |
| J4 | Missing prior literature | LIMITATION | Same as AC15 (L17 + list for the prose writer). |
| J5 | Prereg outcome never stated | FIXED | Same as AC1 (Sec. A, "Preregistered outcome"). |
| J6 | Confidence barely varies; Sonnet slope rests on 16 failures | FIXED + LIMITATION | Same as AC10; L13. |
| J7 | No fixability ceiling | LIMITATION | Same as AC6; L1. |
| J8 | Traps ambiguous by design; degenerate vs other traps pooled | FIXED + LIMITATION | Same as AC3/AC6 (Sec. K, trap headline dropped); L2, L15. |
| J9 | Control arm n = 11, causal claim; within-item comparison possible | FIXED | Same as AC7; "same 60 items" rows in Sec. D. |
| J10 | Sandbox not isolated; recall items kept | FIXED + LIMITATION | Same as AC9 (Sec. G); L8, L9. |
| J11 | No multiple-comparison correction | FIXED | Same as AC13 (Sec. B). The Haiku inverse effect is not claimed. |
| J12 | Haiku belief drop 0.32 vs Sonnet 0.05 not analysed | FIXED | Sec. E and headline 4. |
| F1 | Cited files not in the bundle | REBUTTED | All exist in the repo: `sprint/runset.json`, `out/link_bands.json`, `out/recount.txt`, `logs/sonnet_blocks.log`, `tests/`, `harness_patches/`, `fig/link.pdf`, `out/*.jsonl`; freeze commit `8a07d53` is in the repo history. The submission must link the repository (prose writer). |
| F2 | arXiv refs without authors/URLs; partial reading | LIMITATION | L17; the prose writer adds full references with URLs from NOVELTY.md and verifies them. |
| F3 | Timing of freeze vs first model call | REBUTTED | Freeze commit `8a07d53` is dated 2026-11-13 22:06:06 ET (`git log -1 --format=%ci 8a07d53`). The earliest main-arm transcript record (`ts` field) was written 22:06:20 ET after a 10.2 s model call, so that call started about 22:06:10 ET, after the commit; Sonnet started 23:10 ET. PREREG's "~22:15" is approximate; the commit time is authoritative. "Job start 22:00" is the budget job, not a model call. |
| F4 | Headline 2 understates the Haiku non-trap inverse effect | FIXED | Same as AC1: reported in "Preregistered outcome" with its difficulty check; not a headline because it fails the prereg all-items test and the covariate check. |
| F5 | "only" and causal headline 6 overclaim | FIXED | "only" removed; headline 3 states counts without a causal verb (D10). |
| S1 | Headline wording hard-coded | FIXED | `make_results.headlines()` picks every qualitative word from the CIs / counts (53b2a2d); the Sec. A rule text is also computed. |
| S2 | Headline 2 hides a significant inverse effect; prereg rule not applied | FIXED | Same as AC1. |
| S3 | Control comparison untested, unpaired | FIXED + LIMITATION | Same as AC7 (Sec. D Fisher, same-item rows); L5. |
| S4 | Slope CIs drop failed draws | FIXED + LIMITATION | Valid draws shown in the tables and Sec. J; AUROC is the statistic to quote; L13. |
| S5 | "not estimable" rule broken in robust tables | FIXED | `analyze.py --tables-only`: slopes with an outcome class < 5 print "not estimable"; AUROC with < 5 flagged uninformative (`out/results_tables_robust.md`). |
| S6 | Sonnet slope is a two-band contrast; slopes not comparable across models | FIXED | Stated in RESULTS.md link summary; L13. |
| S7 | Pooled estimates depend on chosen trap share; unstratified bootstrap | FIXED | Same as AC4 (Sec. I stratified CIs). |
| S8 | Headline 1 "n = 300" but rates have other denominators; code-change hidden | FIXED | Headline 1 keeps n = 300 items per model and quotes rates; denominators (242/245 correct, 58/55 wrong) in headline 3 and tables; code-change rates in headline 4. |
| S9 | Paired comparison only on pooled set | FIXED | Sec. C by subset (all / non-trap / trap). Old headline 4 dropped. |
| S10 | ECE CIs unreliable | LIMITATION | L12; Brier given for every comparison (Sec. C). |
| S11 | Zero-width bootstrap intervals in small cells | FIXED | "How to read": Wilson intervals are the ones to quote for cells < 30 or rates 0/1 (Wilson tables in every section). |
| S12 | Hundreds of uncorrected CIs | FIXED + LIMITATION | Same as AC13 (Sec. B); L11. |
| S13 | Degenerate split possibly data-dependent | LIMITATION | The group is named in PREREG (Exploratory line); its regex was written after the data: L15. Trap-kind Fisher tests in Sec. K. |
| S14 | Paired FTR only partly paired; low power | FIXED + LIMITATION | Same as AC11; L16. |
| S15 | Held-when-correct confounded with difficulty | FIXED (partly) + LIMITATION | Same as AC2 (Sec. H); L3. |
| S16 | Weak sensitivity test; recall items not removed | FIXED | Sec. G removes recall items (and the union with audit flags). |
| S17 | Recount checks only point estimates of main tables | FIXED | `recount.py` now also checks link AUROCs (all / non-trap), paired differences and red-team counts: 0 mismatches (RESULTS.md recount tail). CIs are not recounted (bootstrap); that remains a limitation of the recount, not of the estimates. |
| S18 | Figures show n and uncertainty inconsistently | FIXED | Same as J3 / AC16a. |
| S19 | Switch rule by completion time; D4 split; paired block only on 'all' | REBUTTED / FIXED | Switch rule: "by completion time (4 parallel shards)" now stated; 24/13 far above 10/5. D4 disclosed. Paired by subset added (Sec. C). |
