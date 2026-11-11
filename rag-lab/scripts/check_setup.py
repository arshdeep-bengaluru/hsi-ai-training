"""Pre-workshop setup check. Run it the day before, from the rag-lab folder:

    python scripts/check_setup.py          # quick check
    python scripts/check_setup.py --deep   # also one real embedding and one real model call

It prints PASS / WARN / FAIL for each item, with the fix for anything that fails.
Exit code 0 means no FAIL. Needs only the Python standard library to run.
"""
import importlib
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from hsi_rag import config  # noqa: E402  (standard library only)

PACKAGES = [
    ("chromadb", "chromadb"), ("ollama", "ollama"), ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"), ("pydantic", "pydantic"), ("yaml", "pyyaml"),
    ("numpy", "numpy"), ("httpx", "httpx"), ("requests", "requests"),
    ("streamlit", "streamlit"), ("pytest", "pytest"),
]

failures = 0


def report(status: str, message: str, fix: str = "") -> None:
    global failures
    if status == "FAIL":
        failures += 1
    print(f"[{status}] {message}")
    if fix and status != "PASS":
        print(f"       fix: {fix}")


def check_python() -> None:
    v = sys.version_info
    label = f"Python {v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) >= (3, 10):
        report("PASS", label)
    else:
        report("FAIL", f"{label} is too old (need 3.10 or newer)",
               "install Python 3.10+ from python.org, then recreate the virtual environment")
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if in_venv:
        report("PASS", "Running inside a virtual environment")
    else:
        report("WARN", "Not inside a virtual environment",
               "activate it first: .venv\\Scripts\\Activate.ps1 (Windows) or source .venv/bin/activate")


def check_tools() -> None:
    for tool, hint in (("git", "install Git for Windows from git-scm.com"),
                       ("ssh", "Windows: Settings > Apps > Optional features > add 'OpenSSH Client'")):
        path = shutil.which(tool)
        if path:
            report("PASS", f"{tool} found")
        else:
            report("FAIL", f"{tool} not found on PATH", hint)


def check_packages() -> None:
    missing = []
    for module, package in PACKAGES:
        try:
            importlib.import_module(module)
        except Exception:
            missing.append(package)
    if missing:
        report("FAIL", "Missing Python packages: " + ", ".join(missing),
               "run: pip install -r requirements.txt")
    else:
        report("PASS", f"All {len(PACKAGES)} Python packages import")


def ollama_models() -> list[str]:
    url = config.OLLAMA_HOST.rstrip("/") + "/api/tags"
    with urllib.request.urlopen(url, timeout=5) as response:
        return [m["name"] for m in json.load(response)["models"]]


def has_model(models: list[str], wanted: str) -> bool:
    wanted = wanted if ":" in wanted else wanted + ":latest"
    return wanted in models


def check_ollama() -> bool:
    try:
        models = ollama_models()
    except Exception as exc:
        report("FAIL", f"Cannot reach Ollama at {config.OLLAMA_HOST} ({type(exc).__name__})",
               "open the tunnel in another terminal: ssh -L 11434:localhost:11434 <user>@<ec2-host>")
        return False
    report("PASS", f"Ollama reachable at {config.OLLAMA_HOST} ({len(models)} models)")
    for label, name in (("LLM", config.LLM_MODEL), ("Embedding model", config.EMBED_MODEL)):
        if has_model(models, name):
            report("PASS", f"{label} available: {name}")
        else:
            report("FAIL", f"{label} not on the server: {name}",
                   "tell the facilitator, or set LLM_MODEL / EMBED_MODEL to a model in this list: "
                   + ", ".join(models))
    return True


def check_deep() -> None:
    try:
        from hsi_rag import llm
        vectors = llm.embed(["hello"])
        report("PASS", f"Real embedding works (vector length {len(vectors[0])})")
        reply = llm.chat("Reply with the single word OK.")
        report("PASS", f"Real model call works (reply: {reply.strip()[:40]!r})")
    except Exception as exc:
        report("FAIL", f"Real model call failed: {type(exc).__name__}: {exc}",
               "check the tunnel and the model names; see docs/troubleshooting.md")


def check_tests_collect() -> None:
    proc = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q"],
                          cwd=ROOT, capture_output=True, text=True)
    last = (proc.stdout.strip().splitlines() or [""])[-1]
    if proc.returncode == 0:
        report("PASS", f"Tests are discoverable ({last})")
    else:
        report("FAIL", "pytest could not collect the tests",
               "run it from the rag-lab folder with the virtual environment active; see docs/troubleshooting.md")


def main() -> int:
    print(f"HSI RAG Lab setup check  (folder: {ROOT})\n")
    check_python()
    check_tools()
    check_packages()
    reachable = check_ollama()
    if "--deep" in sys.argv:
        if reachable:
            check_deep()
        else:
            report("WARN", "Skipping --deep checks because Ollama is not reachable")
    check_tests_collect()
    print()
    if failures:
        print(f"{failures} problem(s) found. Fix every [FAIL] above and run this again.")
        return 1
    print("All required checks passed. You are ready for the workshop.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
