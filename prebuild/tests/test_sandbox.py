from harness.sandbox import run_tests

T = [{"args": "[2, 3]", "expected": "5", "atol": 0}, {"args": "[0, 0]", "expected": "0", "atol": 0}]


def test_pass_and_fail_per_test():
    assert run_tests("def add(a, b):\n    return a + b\n", "add", T).passed == [True, True]
    r = run_tests("def add(a, b):\n    return a * b + 0\n", "add", T)
    assert r.passed == [False, True] and not r.all_passed


def test_float_tolerance():
    t = [{"args": "[0.1, 0.2]", "expected": "0.3", "atol": 0}]
    assert run_tests("def add(a, b):\n    return a + b\n", "add", t).all_passed


def test_per_test_timeout_does_not_hang():
    code = "def add(a, b):\n    while a == 2: pass\n    return a + b\n"
    r = run_tests(code, "add", T, per_test=1, timeout=120)  # Windows: thread fallback is slow under GIL contention
    assert r.passed == [False, True]


def test_syntax_error_and_missing_function():
    assert not run_tests("def add(a, b) return", "add", T).all_passed
    assert not run_tests("def other(): pass\n", "add", T).all_passed


def test_whole_run_timeout():
    r = run_tests("import time\ntime.sleep(30)\n", "add", T, timeout=3)
    assert r.error == "timeout" and not r.all_passed


def test_inf_literal():
    t = [{"args": "[]", "expected": "inf", "atol": 0}]
    assert run_tests("def f():\n    return float('inf')\n", "f", t).all_passed
