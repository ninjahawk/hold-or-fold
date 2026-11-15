from harness import prompts


def test_parse_confidence():
    assert prompts.parse_confidence("blah\nCONFIDENCE: 85") == 85
    assert prompts.parse_confidence("Confidence: 90%\n...\nCONFIDENCE: 40") == 40
    assert prompts.parse_confidence("**CONFIDENCE:** 70") == 70
    assert prompts.parse_confidence("CONFIDENCE: 150") == 100
    assert prompts.parse_confidence("no number") is None


def test_extract_code():
    t = "x\n```python\ndef f():\n    return 1\n```\nand\n```python\ndef f():\n    return 2\n```"
    assert "return 2" in prompts.extract_code(t)
    assert prompts.extract_code("none") is None


def test_rebuttals_escalate():
    rs = [prompts.rebuttal_prompt(k) for k in range(3)]
    assert "re-check" in rs[0] and "reviewer" in rs[1] and "Fix it" in rs[2]
    assert all("CONFIDENCE" in r for r in rs)
    assert all(prompts.rebuttal_prompt(k, arm="neutral").startswith(prompts.REBUTTALS[0]) for k in range(3))
