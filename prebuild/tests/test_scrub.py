import os
import subprocess
import sys

from conftest import ROOT

SCAN = os.path.join(ROOT, "scrub", "scan.py")


def _scan(d, *extra):
    return subprocess.run([sys.executable, SCAN, str(d), *extra], capture_output=True, text=True, encoding="utf-8", errors="replace")


def test_finds_paths_emails_and_terms(tmp_path):
    (tmp_path / "a.txt").write_text("see C:" + "\\Users\\bob\\x and /" + "srv/x and bob" + "@example.org")
    r = _scan(tmp_path)
    assert r.returncode == 1
    for kind in ("windows_user_path", "unix_private_path", "email"):
        assert kind in r.stdout
    (tmp_path / "a.txt").write_text("hello zzqx world")
    (tmp_path / "terms.sha256").write_text("")
    subprocess.run([sys.executable, "-c",
                    "import hashlib;open(r'%s','w').write(hashlib.sha256(b'zzqx').hexdigest()+'\\n')" % (tmp_path / "t.sha")], check=True)
    r = _scan(tmp_path, "--terms", str(tmp_path / "t.sha"))
    assert r.returncode == 1 and "private_term" in r.stdout


def test_clean_tree_passes(tmp_path):
    (tmp_path / "a.py").write_text("x = 1  # nothing here\n")
    assert _scan(tmp_path).returncode == 0
