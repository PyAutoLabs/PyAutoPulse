from copy import deepcopy

import pytest
import yaml

from pulse import board, decisions


def row(key="solver", day="2026-10-08", repo="PyAutoPulse"):
    return {
        "id": key,
        "title": "NNLS <solver> & choice",
        "date": day,
        "url": f"https://github.com/PyAutoLabs/{repo}/blob/main/decisions/{key}.md",
    }


def write(root, rows):
    (root / "decisions.yaml").write_text(yaml.safe_dump({"decisions": rows}))
    (root / "decisions").mkdir(exist_ok=True)
    for item in rows:
        (root / "decisions" / f"{item['id']}.md").write_text(
            f"# {item['title']}\n\nDate: {item['date']}\n"
        )


def test_records_sorted_and_cross_organ_has_one_canonical_url(tmp_path):
    rows = [row("old", "2026-09-01"), row("new", repo="PyAutoInsight")]
    write(tmp_path, rows)
    (tmp_path / "decisions/new.md").unlink()
    loaded = decisions.load(tmp_path)
    assert [r["id"] for r in loaded] == ["new", "old"]
    html = decisions.render_html(loaded)
    assert 'target="_blank" rel="noopener"' in html
    assert "NNLS &lt;solver&gt; &amp; choice" in html
    assert "NNLS <solver>" not in html
    assert loaded[0]["url"] in html
    assert loaded[0]["url"] in decisions.markdown(loaded)


@pytest.mark.parametrize(
    "mutation",
    [
        {"url": "javascript:alert(1)"},
        {"url": "https://github.com.evil/PyAutoLabs/PyAutoPulse/blob/main/decisions/solver.md"},
        {"url": "https://github.com/PyAutoLabs/PyAutoPulse/blob/main/decisions/other.md"},
        {"date": "2026-02-30"},
        {"date": "2026-1-01"},
        {"id": "../escape"},
        {"title": "bad\nheading"},
        {"extra": "typo"},
    ],
)
def test_invalid_index_rejected(tmp_path, mutation):
    entry = row()
    entry.update(mutation)
    (tmp_path / "decisions.yaml").write_text(yaml.safe_dump({"decisions": [entry]}))
    with pytest.raises(ValueError):
        decisions.load(tmp_path)


def test_duplicate_missing_and_mismatched_owned_records(tmp_path):
    entry = row()
    write(tmp_path, [entry, deepcopy(entry)])
    with pytest.raises(ValueError, match="duplicate"):
        decisions.load(tmp_path)
    write(tmp_path, [entry])
    (tmp_path / "decisions/solver.md").write_text("# Different\nDate: 2026-10-08\n")
    with pytest.raises(ValueError, match="differ"):
        decisions.load(tmp_path)
    (tmp_path / "decisions/solver.md").unlink()
    with pytest.raises(ValueError, match="Missing"):
        decisions.load(tmp_path)


def test_board_disclosure_and_markdown_include_history(monkeypatch):
    monkeypatch.setattr(decisions, "load", lambda: [row(repo="PyAutoInsight")])
    html = board.render_html([])
    assert 'href="#decision-history"' in html
    assert 'id="decision-history"' in html
    assert "NNLS &lt;solver&gt; &amp; choice" in html
    assert "Decision History" in board.render_markdown([])
    assert row(repo="PyAutoInsight")["url"] in board.render_markdown([])
    monkeypatch.setattr(decisions, "load", lambda: [])
    assert "No decisions recorded yet." in board.render_html([])


def test_cli_rejects_invalid_decision_index(monkeypatch, capsys):
    from pulse import cli

    def invalid():
        raise ValueError("broken decision index")

    monkeypatch.setattr(decisions, "load", invalid)
    assert cli.main(["check", "--offline"]) == 1
    assert "FAIL decisions: broken decision index" in capsys.readouterr().out


# ----------------------------------------------------------- designation ---


def designation(key="imaging-delaunay-gpu", **extra):
    entry = row(key)
    entry.update(
        kind="designation",
        likelihood="imaging/delaunay",
        regime="standard",
        hardware_class="gpu_a100",
        optimal="jax_gpu_dense_fp64",
        secondary=["jax_gpu_sparse_fp64"],
        evidence=["imaging-delaunay-hst-a100-runtime"],
        rule="Any imaging Delaunay fit on an A100 uses the dense JAX route.",
        supersedes=None,
    )
    entry.update(extra)
    return entry


def test_designation_entries_validate_and_resolve(tmp_path):
    first = designation("first", date="2026-10-01")
    second = designation("second", supersedes="first", secondary=[])
    write(tmp_path, [first, second, row("plain")])
    loaded = decisions.load(tmp_path)
    assert {r["id"] for r in loaded} == {"first", "second", "plain"}
    assert decisions.ids(tmp_path) == {"first", "second", "plain"}
    assert next(r for r in loaded if r["id"] == "second")["supersedes"] == "first"
    assert "NNLS &lt;solver&gt;" in decisions.render_html(loaded)


@pytest.mark.parametrize(
    "mutation,needle",
    [
        ({"kind": "ranking"}, "kind must be designation"),
        ({"hardware_class": "a100"}, "hardware_class"),
        ({"likelihood": "imaging"}, "likelihood"),
        ({"likelihood": "pixelized/delaunay"}, "likelihood"),
        ({"optimal": "jax_gpu_dense"}, "canonical setup_id"),
        ({"optimal": "jax_gpu_dense_fp64_na"}, "canonical setup_id"),
        ({"secondary": ["numba_cpu_sparse_fp32"]}, "canonical setup_id"),
        ({"secondary": "jax_cpu_dense_fp64"}, "secondary must be a list"),
        ({"secondary": ["jax_gpu_dense_fp64"]}, "distinct"),
        ({"evidence": []}, "evidence"),
        ({"rule": "two\nlines"}, "single-line"),
        ({"supersedes": "missing"}, "supersedes unknown"),
    ],
)
def test_invalid_designations_rejected(tmp_path, mutation, needle):
    entry = designation(**mutation)
    write(tmp_path, [entry])
    with pytest.raises(ValueError, match=needle):
        decisions.load(tmp_path)


def test_designation_fields_require_the_kind(tmp_path):
    entry = designation()
    entry.pop("kind")
    write(tmp_path, [entry])
    with pytest.raises(ValueError, match="requires id, title, date and url"):
        decisions.load(tmp_path)
    entry = designation()
    entry.pop("rule")
    write(tmp_path, [entry])
    with pytest.raises(ValueError, match="lacks rule"):
        decisions.load(tmp_path)


def test_the_live_index_holds_the_day_zero_designations():
    # Likelihood-lifecycle phase 3 (PyAutoPulse#83): the human recorded 39 designations on
    # 2026-10-31 and held datacube/delaunay gpu_a100, which does not separate.
    designations = [r for r in decisions.load() if r.get("kind") == "designation"]
    assert len(designations) == 39
    assert len({(r["likelihood"], r["regime"], r["hardware_class"]) for r in designations}) == 39
    assert all(r["date"] == "2026-10-31" and r["supersedes"] is None for r in designations)
    assert "datacube-delaunay-standard-gpu-a100" not in {r["id"] for r in designations}
