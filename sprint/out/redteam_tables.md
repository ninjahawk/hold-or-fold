## A. Preregistered outcome rules applied (PREREG 'What would change the conclusion')

| model | subset | FTW_3 | FTR_3 | held slope [CI] | fixed slope [CI] | held AUROC [CI] | fixed AUROC [CI] | rule outcome |
|---|---|---|---|---|---|---|---|---|
| Haiku 5.5 | all | 0.08 | 0.36 | 0.81 [0.45, 1.48] | -0.28 [-1.03, 0.20] | 0.78 [0.67, 0.88] | 0.39 [0.24, 0.55] | held slope > 0; fixed slope negative but CI includes 0: stubbornness NOT established |
| Haiku 5.5 | nontrap | 0.07 | 0.35 | 0.88 [0.49, 1.77] | -0.41 [-2.09, 0.12] | 0.82 [0.70, 0.93] | 0.28 [0.12, 0.48] | stubbornness pattern by AUROC (held AUROC > 0.5, fixed AUROC < 0.5, CIs exclude 0.5); fixed slope CI includes 0 |
| Sonnet 5.5 | all | 0.07 | 0.40 | 2.10 [1.10, 4.07] | 0.27 [-0.81, 2.79] | 0.81 [0.71, 0.90] | 0.57 [0.42, 0.74] | held slope > 0; fixed slope CI includes 0 (no link either way) |
| Sonnet 5.5 | nontrap | 0.04 | 0.35 | 2.35 [1.33, 5.07] | 0.08 [-3.61, 3.49] | 0.88 [0.78, 0.95] | 0.47 [0.19, 0.76] | held slope > 0; fixed slope CI includes 0 (no link either way) |

Rule 2 (capitulation: FTW_3 high and similar to FTR_3): FTW_3 = 0.07-0.08, FTR_3 = 0.36-0.40; the FTW_3 and FTR_3 CIs do not overlap for either model, so rule 2 is not met. Rule 1 (null on capitulation: FTW_3 near 0 and FTR_3 high): FTW_3 is below 0.10 for both models while FTR_3 is below 0.5. The preregistered test of the key analysis is on ALL items (PREREG); the non-trap row is the preregistered trap/non-trap split.

## B. Confirmatory family (6 tests: primary contrast and the two key-analysis AUROCs per model, all items), bootstrap p-values (2000 resamples, seed 0) with Holm correction

| test | estimate [95% CI] | null | p (bootstrap) | p (Holm) |
|---|---|---|---|---|
| Haiku 5.5 FTR_3 - FTW_3 (all) | 0.28 [0.17, 0.42] | 0 | 0.000 | 0.000 |
| Haiku 5.5 held AUROC (all) | 0.78 [0.67, 0.88] | 0.5 | 0.000 | 0.000 |
| Haiku 5.5 fixed AUROC (all) | 0.39 [0.24, 0.55] | 0.5 | 0.178 | 0.356 |
| Sonnet 5.5 FTR_3 - FTW_3 (all) | 0.33 [0.21, 0.47] | 0 | 0.000 | 0.000 |
| Sonnet 5.5 held AUROC (all) | 0.81 [0.71, 0.90] | 0.5 | 0.000 | 0.000 |
| Sonnet 5.5 fixed AUROC (all) | 0.57 [0.42, 0.74] | 0.5 | 0.344 | 0.356 |

Bootstrap p-values are resolution-limited: p = 0.000 means no resample crossed the null (p < 0.001).

## C. Sonnet - Haiku, paired, by subset (bootstrap over shared items)

| subset | n | acc0 | mean_conf0 | overconf | brier | ftw_3 | ftr_3 | contrast_3 |
|---|---|---|---|---|---|---|---|---|
| all | 300 | 0.010 [-0.010, 0.030] | 0.050 [0.040, 0.060] | 0.040 [0.018, 0.062] | -0.001 [-0.017, 0.017] | -0.013 [-0.050, 0.021] | 0.038 [-0.118, 0.195] | 0.051 [-0.118, 0.209] |
| nontrap | 260 | 0.019 [0.004, 0.038] | 0.053 [0.041, 0.065] | 0.034 [0.016, 0.050] | -0.013 [-0.025, -0.002] | -0.023 [-0.057, 0.008] | -0.009 [-0.282, 0.255] | 0.014 [-0.259, 0.277] |
| trap | 40 | -0.050 [-0.175, 0.051] | 0.031 [0.015, 0.048] | 0.081 [-0.030, 0.206] | 0.081 [-0.014, 0.183] | 0.238 [-0.137, 0.567] | 0.078 [-0.100, 0.251] | -0.160 [-0.501, 0.221] |

Within-pair: on the 51 items BOTH models got wrong at the confidence turn, Haiku fixed 15 and Sonnet 19 by rebuttal 3 (discordant pairs: Sonnet-only 10, Haiku-only 6; exact McNemar p = 0.454). On the 238 items both got right, Haiku broke 17 and Sonnet 13 (discordant: Sonnet-only 6, Haiku-only 10; p = 0.454).

## D. Main arm (escalating) vs control arm (3x neutral re-check)

| model | subset | main FTR_3 k/n | control FTR_3 k/n | Fisher p | main FTW_3 k/n | control FTW_3 k/n | Fisher p |
|---|---|---|---|---|---|---|---|
| Haiku 5.5 | all | 21/58 | 0/11 | 0.015 | 19/242 | 0/49 | 0.052 |
| Haiku 5.5 | nontrap | 11/31 | 0/7 | 0.084 | 15/229 | 0/48 | 0.082 |
| Haiku 5.5 | same 60 items | 8/12 | 0/11 | 0.001 | 3/48 | 0/49 | 0.117 |
| Sonnet 5.5 | all | 22/55 | 1/11 | 0.081 | 16/245 | 0/49 | 0.083 |
| Sonnet 5.5 | nontrap | 9/26 | 1/7 | 0.397 | 10/234 | 0/48 | 0.221 |
| Sonnet 5.5 | same 60 items | 3/9 | 1/11 | 0.285 | 3/51 | 0/49 | 0.243 |

The control arm is a separate run (fresh solve), so its originally-wrong set differs from the main arm's even on the same 60 items. The control removes the content of rebuttals 2-3 (a claim that the code fails), so it separates 'being told it fails' from 'being asked again', not pressure from information.

## E. What happens to originally-correct work at rebuttal 3 (code, belief, breakage)

| model | n correct0 | code changed (sha) | semantic change (AST, no comments/docstrings) | confidence drop >= 20 pts | conf3 <= 50 | broke (FTW_3) | broke given semantic change |
|---|---|---|---|---|---|---|---|
| Haiku 5.5 | 242 | 102 (42%) | 100 (41%) | 190 (79%) | 94 (39%) | 19 (8%) | 19/100 |
| Sonnet 5.5 | 245 | 124 (51%) | 124 (51%) | 12 (5%) | 2 (1%) | 16 (7%) | 16/124 |

## F. Measurement checks

- Haiku 5.5: solution edited during the confidence turn in 0/300 items (0 of these changed the hidden-test result; y0 is measured after the confidence turn, as preregistered). Originally-wrong items: median share of hidden tests passed 0.97 (non-trap 0.80); 44/58 pass >= 80% of hidden tests (near misses). Distinct initial-confidence values: 20. AUROC of c0 for initial correctness (discrimination): 0.64. Execution errors recorded on any turn: 0.
- Sonnet 5.5: solution edited during the confidence turn in 0/300 items (0 of these changed the hidden-test result; y0 is measured after the confidence turn, as preregistered). Originally-wrong items: median share of hidden tests passed 0.97 (non-trap 0.77); 40/55 pass >= 80% of hidden tests (near misses). Distinct initial-confidence values: 16. AUROC of c0 for initial correctness (discrimination): 0.64. Execution errors recorded on any turn: 0.

## G. Sensitivity: without 'recall' items (memorised public tests) and without any audit-flagged item

| model | set | n | FTR_3 - FTW_3 [CI] | held AUROC [CI] | fixed AUROC [CI] | acc0 | overconf |
|---|---|---|---|---|---|---|---|
| Haiku 5.5 | all | 300 | 0.28 [0.17, 0.42] | 0.78 [0.67, 0.88] | 0.39 [0.24, 0.55] | 0.81 | 0.07 |
| Haiku 5.5 | without own recall items | 256 | 0.25 [0.11, 0.40] | 0.78 [0.66, 0.89] | 0.41 [0.24, 0.60] | 0.82 | 0.06 |
| Haiku 5.5 | without recall or audit-flagged items of EITHER model | 227 | 0.30 [0.14, 0.46] | 0.77 [0.64, 0.88] | 0.40 [0.22, 0.57] | 0.82 | 0.06 |
| Sonnet 5.5 | all | 300 | 0.33 [0.21, 0.47] | 0.81 [0.71, 0.90] | 0.57 [0.42, 0.74] | 0.82 | 0.11 |
| Sonnet 5.5 | without own recall items | 269 | 0.33 [0.19, 0.48] | 0.82 [0.73, 0.90] | 0.55 [0.39, 0.72] | 0.83 | 0.10 |
| Sonnet 5.5 | without recall or audit-flagged items of EITHER model | 227 | 0.34 [0.20, 0.50] | 0.81 [0.71, 0.89] | 0.49 [0.31, 0.68] | 0.82 | 0.10 |

## H. Link with item-difficulty covariates (logistic, slope of c0 per 0.1; bootstrap 2000, seed 0)

Covariates: the OTHER model's correctness at the confidence turn on the same item (difficulty proxy), benchmark (HumanEval+ = 1), trap (1). AUROC within benchmark strata is given as a second check.

| model | outcome | n | c0 slope, no covariates [CI] | c0 slope, with covariates [CI] (valid draws) | AUROC MBPP+ (n) | AUROC HumanEval+ (n) |
|---|---|---|---|---|---|---|
| Haiku 5.5 | held | 242 | 0.81 [0.43, 1.50] | 0.88 [0.52, 1.77] (1201) | 0.73 (164) | 0.94 (78) |
| Haiku 5.5 | fixed | 58 | -0.28 [-1.05, 0.18] | -0.02 [-0.91, 0.56] (1172) | 0.39 (48) | 0.40 (10) |
| Sonnet 5.5 | held | 245 | 2.10 [1.12, 4.10] | 2.12 [1.07, 4.89] (1587) | 0.76 (166) | 0.91 (79) |
| Sonnet 5.5 | fixed | 55 | 0.27 [-0.79, 2.56] | 0.31 [-1.05, 3.24] (1051) | 0.65 (46) | 0.25 (9) |

## I. Primary contrast, bootstrap stratified by trap / non-trap (design fixes 40 traps)

- Haiku 5.5: FTR_3 - FTW_3 = 0.28 [0.16, 0.42] (stratified), vs 0.17-0.42 unstratified.
- Sonnet 5.5: FTR_3 - FTW_3 = 0.33 [0.20, 0.46] (stratified), vs 0.21-0.47 unstratified.

## J. Valid bootstrap draws behind each link slope CI (of 2000; dropped draws = class < 5 or no MLE)

| model | subset | held slope | fixed slope | pooled slope |
|---|---|---|---|---|
| Haiku 5.5 | all | 2000 | 2000 | 2000 |
| Haiku 5.5 | nontrap | 1997 | 1973 | 2000 |
| Sonnet 5.5 | all | 2000 | 2000 | 2000 |
| Sonnet 5.5 | nontrap | 1942 | 1884 | 2000 |

## K. Trap fixes by trap kind (degenerate-input regex fixed in analyze.py; group named in PREREG as exploratory)

- Haiku 5.5: fixed 8/13 wrong degenerate-input traps vs 2/14 other wrong traps (Fisher p = 0.018).
- Sonnet 5.5: fixed 11/14 wrong degenerate-input traps vs 2/15 other wrong traps (Fisher p = 0.001).

## L. Re-execution of the confidence-turn and rebuttal-3 solutions (once more, 8 parallel workers)

1200 executions; recorded vs re-executed hidden-test pass differs in 0: none.

