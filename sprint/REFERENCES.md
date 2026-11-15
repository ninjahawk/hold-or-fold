# Verified references (for the report writer)

Each entry below was checked on 2026-11-14 against the arXiv API record (export.arxiv.org/api/query?id_list=<id>):
the title, authors and first-submission date come from that record. The venue notes come from the search results and say so.
This resolves REDTEAM rows AC15, J4 (the prior work the reviewers named) and F2 (the two closest papers had no authors or URLs).
The other entries in `prebuild/RELATED.md` were checked on their arXiv abstract pages on 2026-11-11.
Cite only from this list or RELATED.md. Any claim about a paper's content beyond its abstract still needs reading at the source.

## Closest prior work (cite as concurrent; see NOVELTY.md for the safe novelty wording)
- Bui, N. D. Q. (2026). Thinking-in-Bets at Test Time Reduces Sycophantic Revisions in LLM Agents. arXiv:2610.34654 (submitted 2026-10-26). https://arxiv.org/abs/2610.34654
- Rodrigues, C., Rodrigues, C., & Reddy G, A. (2026). Done Is Not Correct: Measuring Silent Failures and Self-Verification Calibration When LLM Agents Take CAD Actions. arXiv:2611.10063 (submitted 2026-11-06). https://arxiv.org/abs/2611.10063

## Answer flipping and sycophancy under challenge
- Laban, P., Murakhovs'ka, L., Xiong, C., & Wu, C.-S. (2023). Are You Sure? Challenging LLMs Leads to Performance Drops in The FlipFlop Experiment. arXiv:2311.08596. https://arxiv.org/abs/2311.08596
- Wang, B., Yue, X., & Sun, H. (2023). Can ChatGPT Defend its Belief in Truth? Evaluating LLM Reasoning via Debate. arXiv:2305.13160. Venue per search results: Findings of EMNLP 2023. https://arxiv.org/abs/2305.13160
- Xie, Q., Wang, Z., Feng, Y., & Xia, R. (2023). Ask Again, Then Fail: Large Language Models' Vacillations in Judgment. arXiv:2310.02174. https://arxiv.org/abs/2310.02174
- Sharma, M., Tong, M., Korbak, T., et al. (19 authors) (2023). Towards Understanding Sycophancy in Language Models. arXiv:2310.13548. https://arxiv.org/abs/2310.13548

## Stated confidence and calibration
- Kadavath, S., Conerly, T., Askell, A., et al. (36 authors) (2022). Language Models (Mostly) Know What They Know. arXiv:2207.05221. https://arxiv.org/abs/2207.05221
- Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2023). Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs. arXiv:2306.13063. Venue per its arXiv comment (v2): ICLR 2024. https://arxiv.org/abs/2306.13063

## BibTeX
```bibtex
@misc{bui2026bets, author={Nghi D. Q. Bui}, title={Thinking-in-Bets at Test Time Reduces Sycophantic Revisions in {LLM} Agents}, year={2026}, eprint={2610.34654}, archivePrefix={arXiv}}
@misc{rodrigues2026done, author={Carson Rodrigues and Clive Rodrigues and Aravind Reddy G}, title={Done Is Not Correct: Measuring Silent Failures and Self-Verification Calibration When {LLM} Agents Take {CAD} Actions}, year={2026}, eprint={2611.10063}, archivePrefix={arXiv}}
@misc{laban2023flipflop, author={Philippe Laban and Lidiya Murakhovs'ka and Caiming Xiong and Chien-Sheng Wu}, title={Are You Sure? Challenging {LLMs} Leads to Performance Drops in The {FlipFlop} Experiment}, year={2023}, eprint={2311.08596}, archivePrefix={arXiv}}
@misc{wang2023defend, author={Boshi Wang and Xiang Yue and Huan Sun}, title={Can {ChatGPT} Defend its Belief in Truth? Evaluating {LLM} Reasoning via Debate}, year={2023}, eprint={2305.13160}, archivePrefix={arXiv}}
@misc{xie2023askagain, author={Qiming Xie and Zengzhi Wang and Yi Feng and Rui Xia}, title={Ask Again, Then Fail: Large Language Models' Vacillations in Judgment}, year={2023}, eprint={2310.02174}, archivePrefix={arXiv}}
@misc{sharma2023sycophancy, author={Mrinank Sharma and Meg Tong and Tomasz Korbak and others}, title={Towards Understanding Sycophancy in Language Models}, year={2023}, eprint={2310.13548}, archivePrefix={arXiv}}
@misc{kadavath2022know, author={Saurav Kadavath and Tom Conerly and Amanda Askell and others}, title={Language Models (Mostly) Know What They Know}, year={2022}, eprint={2207.05221}, archivePrefix={arXiv}}
@misc{xiong2023uncertainty, author={Miao Xiong and Zhiyuan Hu and Xinyang Lu and Yifei Li and Jie Fu and Junxian He and Bryan Hooi}, title={Can {LLMs} Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in {LLMs}}, year={2023}, eprint={2306.13063}, archivePrefix={arXiv}}
```
