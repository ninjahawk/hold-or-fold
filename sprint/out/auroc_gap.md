# AUROC gap test (POST-HOC, added after review 11-15, not preregistered)

Stratified bootstrap (originally-correct and originally-wrong items resampled separately), 10000 replicates, seed 0, 95% percentile CI, two-sided bootstrap p (2 x min tail share; resolution 1/10000), Holm over 2 models.

| model | AUROC_hold (n, held) | AUROC_fix (n, fixed) | gap [95% CI] | p | p (Holm) | distance-from-0.5 gap [95% CI] | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| Haiku 5.5 | 0.78 (242, 223) | 0.39 (58, 21) | 0.39 [0.20, 0.57] | 0.0002 (0.000) | 0.0004 (0.000) | 0.17 [-0.02, 0.33] | 0.0738 (0.074) | 0.0738 (0.074) |
| Sonnet 5.5 | 0.81 (245, 229) | 0.57 (55, 22) | 0.24 [0.06, 0.42] | 0.0078 (0.008) | 0.0078 (0.008) | 0.24 [0.06, 0.35] | 0.0078 (0.008) | 0.0156 (0.016) |

p = 0.0000 means no replicate crossed 0 (p < 0.0001 at this resolution).
