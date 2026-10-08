"""bin/pyauto-pulse: check, board, census, fetch."""

import json

import pytest
from conftest import SHA_A, SHA_B, fixture_doc

from pulse import cli

GH = "PyAutoLabs/autolens_profiling"
PATH = "dashboard/summary.json"


@pytest.fixture
def argv(registry_file, fake_mind, tmp_path):
    out = tmp_path / "organ"
    out.mkdir()

    def make(cmd, *extra):
        return [
            "--registry",
            str(registry_file),
            cmd,
            "--mind",
            str(fake_mind),
            "--out",
            str(out),
            *extra,
        ]

    make.out = out
    return make


def test_board_then_check_online_and_offline(argv, web, capsys):
    web.publish(GH, SHA_A, PATH, fixture_doc("lens_summary_v1.json"))
    assert cli.main(argv("board")) == 0
    for name in ("dashboard.md", "dashboard.html", "badge.json", "state.json"):
        assert (argv.out / name).is_file()
    assert (argv.out / "receipts" / "lens.json").is_file()
    assert (argv.out / "snapshots" / "lens.json").is_file()
    capsys.readouterr()
    assert cli.main(argv("check")) == 0
    assert capsys.readouterr().out.rstrip().endswith("check: OK")
    web.down = True
    assert cli.main(argv("check", "--offline")) == 0
    assert "check: OK" in capsys.readouterr().out


def test_state_json_passes_the_brain_validator(argv, web):
    web.publish(GH, SHA_A, PATH, fixture_doc("lens_summary_v1.json"))
    cli.main(argv("board"))
    validator = cli._state_validator()
    if validator is None:
        pytest.skip("no PyAutoBrain checkout here")
    state = json.loads((argv.out / "state.json").read_text())
    assert validator.validate_state(state) == []
    assert json.loads((argv.out / "badge.json").read_text())["label"] == "pulse"


def test_check_fails_when_the_dashboard_is_behind_the_receipt(argv, web, capsys):
    web.publish(GH, SHA_A, PATH, fixture_doc("lens_summary_v1.json"))
    cli.main(argv("board"))
    web.publish(GH, SHA_B, PATH, fixture_doc("lens_summary_v1.json"))
    capsys.readouterr()
    assert cli.main(argv("check")) == 1
    out = capsys.readouterr().out
    assert "FAIL dashboard: stale for lens" in out and out.rstrip().endswith("check: FAIL")


def test_check_fails_on_an_unavailable_feed_with_no_capture(argv, capsys):
    assert cli.main(argv("check")) == 1
    assert "FAIL lens: unavailable" in capsys.readouterr().out


def test_census_and_fetch(argv, web, capsys):
    web.publish(GH, SHA_A, PATH, fixture_doc("lens_summary_v1.json"))
    assert cli.main(argv("fetch", "--instance", "lens")) == 0
    assert f"lens: ok at {SHA_A[:12]}" in capsys.readouterr().out
    assert not (argv.out / "dashboard.md").exists()  # fetch renders nothing
    web.down = True
    assert cli.main(argv("census")) == 0
    line = capsys.readouterr().out.strip()
    assert line.startswith("lens: 11 records · 5 comparisons · 6 limitations ·")
    assert cli.main(argv("fetch")) == 1


def test_board_from_a_local_file_is_labelled_local(argv, tmp_path, capsys):
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(fixture_doc("valid_empty.json")))
    assert cli.main(argv("board", "--from", f"lens={path}")) == 0
    md = (argv.out / "dashboard.md").read_text()
    assert "**Local read:**" in md and "**No measurements.**" in md
    assert not (argv.out / "receipts").exists()


def test_unknown_instance_is_a_clean_error(argv, capsys):
    assert cli.main(argv("fetch", "--instance", "nope")) == 1
    assert "no instance 'nope'" in capsys.readouterr().err


def test_decision_only_change_requires_regeneration(argv, web, monkeypatch, capsys):
    from pulse import decisions

    web.publish(GH, SHA_A, PATH, fixture_doc("lens_summary_v1.json"))
    monkeypatch.setattr(decisions, "load", lambda: [])
    assert cli.main(argv("board")) == 0
    monkeypatch.setattr(
        decisions,
        "load",
        lambda: [
            {
                "id": "solver",
                "title": "Solver choice",
                "date": "2026-10-08",
                "url": "https://github.com/PyAutoLabs/PyAutoInsight/blob/main/decisions/solver.md",
            }
        ],
    )
    assert cli.main(argv("check", "--offline")) == 1
    assert "FAIL decisions" in capsys.readouterr().out
    assert cli.main(argv("board", "--offline")) == 0
    assert cli.main(argv("check", "--offline")) == 0
