# Novelty check against the two closest papers (read Fri 2026-11-13, sprint time)

Read from the arXiv HTML full text (about 28% and 42% of each read verbatim; the rest via a summary, marked below).

- **Thinking-in-Bets at Test Time Reduces Sycophantic Revisions in LLM Agents** (arXiv 2610.34654, v1 2026-10-26).
  Gemini models (3.5 Flash-Lite, 3.5/3.6/3.8 Flash, 4.0 Argon) on SWE-style and QA benchmarks. It measures false
  reversals of correct work and fixing of real mistakes under pushback, with ground truth (incl. hidden tests on
  SWE-Pushback-Hidden), and elicits per-claim confidences; but it is a mitigation paper, says its confidences are
  "the model's own estimates rather than calibrated probabilities", uses them as a keep/fix threshold, and (in the
  parts read) does not test whether initial confidence predicts who holds and who folds. Pushback is a single bare
  complaint or simulated user feedback, not a fixed escalation ladder.
- **Done Is Not Correct: Measuring Silent Failures and Self-Verification Calibration When LLM Agents Take CAD
  Actions** (arXiv 2611.10063, v1 2026-11-06). 13 CAD tasks (122 checks), four models incl. claude-haiku-4-5 and
  claude-sonnet-4-6; graded verbalized confidence with ECE/AUROC/Brier against checked truth. No rebuttal phase
  ("execution feedback, not a challenge"), no false-reversal measure, no designed confident-wrong items.
- **What differs here:** one item set with both halves joined: graded confidence that the agent's own finished
  code passes hidden tests (calibration), then a fixed three-step escalating rebuttal ladder given to every item
  regardless of correctness, scored by execution after every turn. The new quantity is the link: does the initial
  confidence predict holding when right (no flip-to-wrong) and fixing when wrong (flip-to-right)? Plus trap
  variants built to produce confident-wrong cases, a neutral-only control arm for the escalation confound, and
  current Claude models (Haiku 5.5, Sonnet 5.5) on ~300 public items each.
- **Safe novelty wording:** not "first to measure false reversals" (Thinking-in-Bets does) nor "first to measure
  agent completion calibration" (Done Is Not Correct does). Claim only the calibration-defense link and the joined
  measurement on hidden-test truth with an escalation ladder; cite both as concurrent work.
