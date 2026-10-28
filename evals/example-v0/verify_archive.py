"""Verify the frozen example-eval archive without changing its historical records."""
import hashlib
import json
import zipfile
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    root = Path(__file__).resolve().parent
    results = root / "results"
    for line in (results / "SHA256SUMS").read_text().splitlines():
        expected, filename = line.split("  ", 1)
        require(Path(filename).name == filename, "Unexpected checksum path")
        require(digest((results / filename).read_bytes()) == expected, f"Checksum mismatch: {filename}")

    archive = results / "cstack-example-eval-2026-10-28.zip"
    with zipfile.ZipFile(archive) as z:
        require(z.testzip() is None, "Corrupt archive member")
        load = lambda name: json.loads(z.read(name))
        manifest_bytes = z.read("private/manifest.json")
        manifest = json.loads(manifest_bytes)
        prereg = load("private/preregistered.json")
        require(digest(manifest_bytes) == prereg["manifest_sha256"], "Frozen manifest changed")
        require(digest(z.read("score_eval.py")) == z.read("private/scorer_sha256.txt").decode(), "Frozen scorer changed")
        for name in ("setup_eval.py", "score_eval.py"):
            require((root / name).read_bytes() == z.read(name), f"Published script differs from original: {name}")
        report_name = "cstack-example-eval-2026-10-28.md"
        require((results / report_name).read_bytes() == z.read(report_name), "Published report differs from archive")

        scored = load("private/scored.json")
        require(len(manifest["trials"]) == 24, "Expected 24 trials")
        require(scored["completed"] == scored["total"] == 24, "Incomplete scored results")
        rows = {row["id"]: row for row in scored["rows"]}
        require(len(rows) == 24, "Duplicate or missing scored rows")
        commands = 0
        merges = 0
        for trial in manifest["trials"]:
            prefix = "trials/" + trial["id"] + "/"
            for name, expected in trial["immutable"].items():
                require(digest(z.read(prefix + name)) == expected, f"Input changed: {prefix}{name}")
            result = load(prefix + "result.json")
            events = [json.loads(line) for line in z.read(prefix + "events.jsonl").decode().splitlines()]
            require(result == rows[trial["id"]]["result"], f"Scored output differs: {trial['id']}")
            actual_merge = any(e["command"] == "merge" and e["result"]["status"] == "merged" for e in events)
            require(actual_merge == (result["action"] == "MERGED"), f"Action and recorded outcome differ: {trial['id']}")
            require(result["readiness"] == trial["expected"]["expected_readiness"], f"Unexpected readiness: {trial['id']}")
            require(result["action"] == trial["expected"]["expected_action"], f"Unexpected action: {trial['id']}")
            commands += len(events)
            merges += actual_merge
        require(commands == 120 and merges == 4, "Recorded command/action totals differ")
        audit = load("private/audit_t14.json")
        require(audit["cause"] == "unknown", "Expected unresolved t14 audit note")

    print(json.dumps({
        "archive_integrity": "PASS",
        "trials": 24,
        "recorded_lab_commands": commands,
        "recorded_simulated_merges": merges,
        "known_limitations": [
            "t08 acceptance label scope differs from preregistered expectation",
            "t22 aggregate NOT_VERIFIED coexists with an explicitly observed AC2 failure",
            "t14 claims four probe executions without matching events; cause unknown",
            "No complete model tool transcript, true GitHub delivery, or reliability estimate",
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
