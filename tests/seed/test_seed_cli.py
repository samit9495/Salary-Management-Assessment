import json
import os
import subprocess
import sys
from pathlib import Path


def test_seed_cli_help_lists_required_flags() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "scripts.seed", "--help"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parents[2]),
    )

    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert "--count" in out
    assert "--seed" in out
    assert "--reset" in out


def test_seed_cli_emits_start_and_finish_json_log_lines(tmp_path: Path) -> None:
    db_path = tmp_path / "seed_cli.db"
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{db_path}"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.seed",
            "--count",
            "5",
            "--seed",
            "1",
            "--reset",
        ],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parents[2]),
        env=env,
    )

    assert result.returncode == 0, result.stderr

    json_lines = [
        json.loads(line)
        for line in result.stdout.splitlines()
        if line.startswith("{")
    ]
    events = [entry.get("event") for entry in json_lines]

    assert "seed_start" in events
    assert "seed_finish" in events

    finish = next(entry for entry in json_lines if entry.get("event") == "seed_finish")
    assert finish["inserted"] == 5
