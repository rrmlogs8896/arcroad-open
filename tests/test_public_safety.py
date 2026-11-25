"""Fails if the public copy holds anything that must stay private."""
import pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
BLOCKED_WORDS = re.compile(r"genpact|mythri|\bSTATE\.md\b", re.I)
SECRET = re.compile(r"(api[_-]?key|secret|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}")
BAD_EXT = {".gpx", ".fit", ".kml", ".kmz", ".tcx", ".heic", ".pem", ".key"}
TEXT_EXT = {".html", ".js", ".css", ".json", ".py", ".md", ".txt", ".xml", ".yml", ".yaml", ".toml"}


def files():
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        return [ROOT / f for f in out.splitlines()]
    except Exception:
        return [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]


def test_no_private_file_types():
    bad = [str(p.relative_to(ROOT)) for p in files() if p.suffix.lower() in BAD_EXT]
    assert not bad, bad


def test_no_gated_or_private_folders():
    bad = [str(p.relative_to(ROOT)) for p in files()
           if p.relative_to(ROOT).parts[:2] in {("web", "jury"), ("functions", "jury")} or p.relative_to(ROOT).parts[0] == "research"]
    assert not bad, bad


def test_no_private_words_or_secrets():
    hits = []
    for p in files():
        if p.suffix.lower() not in TEXT_EXT or p.name == "test_public_safety.py" or not p.exists():
            continue
        t = p.read_text(errors="ignore")
        if BLOCKED_WORDS.search(t) or SECRET.search(t):
            hits.append(str(p.relative_to(ROOT)))
    assert not hits, hits
