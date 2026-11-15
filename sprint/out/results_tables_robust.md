
### haiku (claude:claude-haiku-5-5|neutral)

dropped (incomplete or no initial confidence): 0; turns without a parseable CONFIDENCE: 0

| subset | n | wrong0 | acc0 | conf0 | Brier | ECE | overconf | FTW_1 | FTW_2 | FTW_3 | FTR_1 | FTR_2 | FTR_3 | FTR_3-FTW_3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 60 | 11 | 0.82 [0.72, 0.90] | 0.88 [0.85, 0.90] | 0.15 [0.08, 0.23] | 0.10 [0.04, 0.20] | 0.06 [-0.03, 0.16] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| nontrap | 55 | 7 | 0.87 [0.78, 0.95] | 0.88 [0.84, 0.90] | 0.10 [0.05, 0.18] | 0.07 [0.03, 0.16] | 0.00 [-0.07, 0.10] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| trap | 5 | 4 | 0.20 [0.00, 0.60] | 0.90 [0.88, 0.93] | 0.67 [0.34, 0.86] | 0.70 [0.29, 0.93] | 0.70 [0.29, 0.93] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| trap_without_degenerate | 2 | 2 | 0.00 [0.00, 0.00] | 0.88 [0.88, 0.88] | 0.77 [0.77, 0.77] | 0.88 [0.88, 0.88] | 0.88 [0.88, 0.88] | nan | nan | nan | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | nan |
| trap_degenerate_only | 3 | 2 | 0.33 [0.00, 1.00] | 0.92 [0.88, 0.95] | 0.59 [0.01, 0.90] | 0.67 [0.12, 0.95] | 0.59 [-0.12, 0.95] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

Code-change rate by turn k (all items): correct 0.02, 0.04, 0.04; wrong 0.09, 0.09, 0.09. Confidence drop on correct items: -0.01, -0.01, -0.01

Supplementary (not preregistered) raw flip counts k/n with Wilson 95% intervals:

| subset | ftw_1 | ftw_2 | ftw_3 | ftr_1 | ftr_2 | ftr_3 |
|---|---|---|---|---|---|---|
| all | 0/49 [0.00, 0.07] | 0/49 [0.00, 0.07] | 0/49 [0.00, 0.07] | 0/11 [0.00, 0.26] | 0/11 [0.00, 0.26] | 0/11 [0.00, 0.26] |
| nontrap | 0/48 [0.00, 0.07] | 0/48 [0.00, 0.07] | 0/48 [0.00, 0.07] | 0/7 [0.00, 0.35] | 0/7 [0.00, 0.35] | 0/7 [0.00, 0.35] |
| trap | 0/1 [0.00, 0.79] | 0/1 [0.00, 0.79] | 0/1 [0.00, 0.79] | 0/4 [0.00, 0.49] | 0/4 [0.00, 0.49] | 0/4 [0.00, 0.49] |

Calibration-defense link (all items; slope = log-odds per 0.1 confidence):

| outcome | n | n positive | slope [95% CI] | AUROC of c0 [95% CI] |
|---|---|---|---|---|
| held_correct | 49 | 49 | not estimable (outcome class < 5) | nan [nan, nan] |
| fixed_wrong | 11 | 0 | not estimable (outcome class < 5) | nan [nan, nan] |
| pooled_end_correct | 60 | 49 | 0.32 [-1.38, 0.76] (1987/2000 draws) | 0.52 [0.32, 0.71] |

Calibration-defense link (non-trap items; slope = log-odds per 0.1 confidence):

| outcome | n | n positive | slope [95% CI] | AUROC of c0 [95% CI] |
|---|---|---|---|---|
| held_correct | 48 | 48 | not estimable (outcome class < 5) | nan [nan, nan] |
| fixed_wrong | 7 | 0 | not estimable (outcome class < 5) | nan [nan, nan] |
| pooled_end_correct | 55 | 48 | 0.48 [-1.19, 1.00] (1670/2000 draws) | 0.57 [0.30, 0.81] |

Non-trap originally-wrong n = 7 (prereg minimum 15 for non-trap FTR: NOT met, non-trap FTR underpowered). Degenerate-input traps: 3.

### sonnet (claude:claude-sonnet-5-5|neutral)

dropped (incomplete or no initial confidence): 0; turns without a parseable CONFIDENCE: 0

| subset | n | wrong0 | acc0 | conf0 | Brier | ECE | overconf | FTW_1 | FTW_2 | FTW_3 | FTR_1 | FTR_2 | FTR_3 | FTR_3-FTW_3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 60 | 11 | 0.82 [0.72, 0.90] | 0.92 [0.91, 0.93] | 0.16 [0.09, 0.24] | 0.11 [0.04, 0.22] | 0.10 [0.01, 0.21] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.09 [0.00, 0.33] | 0.09 [0.00, 0.33] | 0.09 [0.00, 0.33] | 0.09 [0.00, 0.33] |
| nontrap | 55 | 7 | 0.87 [0.78, 0.96] | 0.92 [0.91, 0.93] | 0.11 [0.04, 0.19] | 0.06 [0.01, 0.15] | 0.05 [-0.03, 0.14] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.14 [0.00, 0.50] | 0.14 [0.00, 0.50] | 0.14 [0.00, 0.50] | 0.14 [0.00, 0.50] |
| trap | 5 | 4 | 0.20 [0.00, 0.60] | 0.93 [0.93, 0.94] | 0.69 [0.35, 0.86] | 0.73 [0.34, 0.93] | 0.73 [0.34, 0.93] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| trap_without_degenerate | 2 | 1 | 0.50 [0.00, 1.00] | 0.94 [0.93, 0.94] | 0.43 [0.00, 0.86] | 0.44 [0.06, 0.93] | 0.44 [-0.06, 0.93] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| trap_degenerate_only | 3 | 3 | 0.00 [0.00, 0.00] | 0.93 [0.93, 0.93] | 0.86 [0.86, 0.86] | 0.93 [0.93, 0.93] | 0.93 [0.93, 0.93] | nan | nan | nan | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | nan |

Code-change rate by turn k (all items): correct 0.06, 0.06, 0.06; wrong 0.09, 0.09, 0.09. Confidence drop on correct items: -0.02, -0.02, -0.02

Supplementary (not preregistered) raw flip counts k/n with Wilson 95% intervals:

| subset | ftw_1 | ftw_2 | ftw_3 | ftr_1 | ftr_2 | ftr_3 |
|---|---|---|---|---|---|---|
| all | 0/49 [0.00, 0.07] | 0/49 [0.00, 0.07] | 0/49 [0.00, 0.07] | 1/11 [0.02, 0.38] | 1/11 [0.02, 0.38] | 1/11 [0.02, 0.38] |
| nontrap | 0/48 [0.00, 0.07] | 0/48 [0.00, 0.07] | 0/48 [0.00, 0.07] | 1/7 [0.03, 0.51] | 1/7 [0.03, 0.51] | 1/7 [0.03, 0.51] |
| trap | 0/1 [0.00, 0.79] | 0/1 [0.00, 0.79] | 0/1 [0.00, 0.79] | 0/4 [0.00, 0.49] | 0/4 [0.00, 0.49] | 0/4 [0.00, 0.49] |

Calibration-defense link (all items; slope = log-odds per 0.1 confidence):

| outcome | n | n positive | slope [95% CI] | AUROC of c0 [95% CI] |
|---|---|---|---|---|
| held_correct | 49 | 49 | not estimable (outcome class < 5) | nan [nan, nan] |
| fixed_wrong | 11 | 1 | not estimable (outcome class < 5) | 0.30 [0.06, 0.58] (outcome class < 5: uninformative) |
| pooled_end_correct | 60 | 50 | 0.58 [-0.61, 2.69] (1969/2000 draws) | 0.64 [0.48, 0.79] |

Calibration-defense link (non-trap items; slope = log-odds per 0.1 confidence):

| outcome | n | n positive | slope [95% CI] | AUROC of c0 [95% CI] |
|---|---|---|---|---|
| held_correct | 48 | 48 | not estimable (outcome class < 5) | nan [nan, nan] |
| fixed_wrong | 7 | 1 | not estimable (outcome class < 5) | 0.50 [0.12, 0.88] (outcome class < 5: uninformative) |
| pooled_end_correct | 55 | 49 | 0.96 [-0.28, 4.08] (1442/2000 draws) | 0.71 [0.49, 0.91] |

Non-trap originally-wrong n = 7 (prereg minimum 15 for non-trap FTR: NOT met, non-trap FTR underpowered). Degenerate-input traps: 3.

### Paired sonnet - haiku (n shared = 60, both wrong at start = 9)

| metric | diff | 95% CI |
|---|---|---|
| acc0 | 0.000 | [-0.067, 0.067] |
| mean_conf0 | 0.043 | [0.022, 0.071] |
| brier | 0.007 | [-0.036, 0.057] |
| ece | 0.015 | [-0.049, 0.079] |
| overconf | 0.043 | [-0.016, 0.107] |
| ftw_3 | 0.000 | [0.000, 0.000] |
| ftr_3 | 0.091 | [0.000, 0.300] |
| contrast_3 | 0.091 | [0.000, 0.300] |
