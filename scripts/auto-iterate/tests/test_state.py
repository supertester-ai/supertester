from pathlib import Path
from state import State, load_or_init


def test_state_init_defaults(tmp_path):
    s = State(state_file=str(tmp_path / "s.json"))
    assert s.phase0_complete is False
    assert s.phase1_converged is False
    assert s.converged_modules == []
    assert s.history == {}


def test_state_save_load_roundtrip(tmp_path):
    path = str(tmp_path / "s.json")
    s = State(state_file=path)
    s.phase0_complete = True
    s.converged_modules.append("URL通用校验")
    s.add_history("phase1", {"iter": 1, "score": 0.65, "patches_applied": 1})
    s.save()

    s2 = load_or_init(path)
    assert s2.phase0_complete is True
    assert "URL通用校验" in s2.converged_modules
    assert s2.history["phase1"][0]["score"] == 0.65


def test_load_or_init_missing_creates_new(tmp_path):
    path = str(tmp_path / "nonexistent.json")
    s = load_or_init(path)
    assert s.phase0_complete is False
    assert s.state_file == path


def test_state_best_score(tmp_path):
    s = State(state_file=str(tmp_path / "s.json"))
    s.add_history("URL", {"iter": 1, "score": 0.60})
    s.add_history("URL", {"iter": 2, "score": 0.82})
    s.add_history("URL", {"iter": 3, "score": 0.75})
    assert s.best_score("URL") == 0.82
