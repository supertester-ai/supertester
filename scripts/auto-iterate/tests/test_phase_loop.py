import json
from unittest.mock import patch, MagicMock
from phase_loop import iterate

@patch('phase_loop.run_analysis_cycle')
@patch('phase_loop.score_artifact')
@patch('phase_loop.patcher')
def test_iterate_converges_first_try(mock_patcher, mock_score, mock_analyze, tmp_path):
    mock_score.return_value = {"total_weighted_score": 0.90, "dimensions": {"a": {"score": 0.70}}, "converged": True}
    convergence = {"min_total_score": 0.85, "min_dimension_score": 0.65, "max_iterations": 3}

    gen_calls = []
    def fake_generator(iter_num):
        gen_calls.append(iter_num)
        return "ai output"

    result = iterate(
        phase="phase1", module_name="_",
        generator=fake_generator,
        baseline_a={}, convergence=convergence,
        skill_dir=str(tmp_path / "skills"),
        snapshot_root=str(tmp_path / "snap"),
        iter_root=str(tmp_path / "iters"),
        abstraction_map={},
        max_revise_attempts=2,
    )
    assert result["converged"] is True
    assert result["iterations"] == 1
    assert len(gen_calls) == 1
    mock_analyze.assert_not_called()

@patch('phase_loop.run_analysis_cycle')
@patch('phase_loop.score_artifact')
@patch('phase_loop.patcher')
def test_iterate_patches_and_retries(mock_patcher, mock_score, mock_analyze, tmp_path):
    mock_score.side_effect = [
        {"total_weighted_score": 0.60, "dimensions": {"a": {"score": 0.50}}, "converged": False},
        {"total_weighted_score": 0.90, "dimensions": {"a": {"score": 0.70}}, "converged": True},
    ]
    mock_analyze.return_value = {
        "verdict": "PASS",
        "patch": {"patches": [{"file": "skills/x.md", "diff": "d"}]},
    }
    mock_patcher.apply_patches.return_value = []
    convergence = {"min_total_score": 0.85, "min_dimension_score": 0.65, "max_iterations": 3}

    gen_iters = []
    def fake_generator(iter_num):
        gen_iters.append(iter_num)
        return "ai output"

    result = iterate(
        phase="phase1", module_name="_",
        generator=fake_generator,
        baseline_a={}, convergence=convergence,
        skill_dir=str(tmp_path / "skills"),
        snapshot_root=str(tmp_path / "snap"),
        iter_root=str(tmp_path / "iters"),
        abstraction_map={},
        max_revise_attempts=2,
    )
    assert result["converged"] is True
    assert result["iterations"] == 2
    assert gen_iters == [1, 2]
    assert mock_patcher.snapshot.called
    assert mock_patcher.apply_patches.called

@patch('phase_loop.run_analysis_cycle')
@patch('phase_loop.score_artifact')
@patch('phase_loop.patcher')
def test_iterate_exhausts_max_iterations(mock_patcher, mock_score, mock_analyze, tmp_path):
    mock_score.return_value = {"total_weighted_score": 0.60, "dimensions": {"a": {"score": 0.50}}, "converged": False}
    mock_analyze.return_value = {
        "verdict": "PASS",
        "patch": {"patches": [{"file": "skills/x.md", "diff": "d"}]},
    }
    mock_patcher.apply_patches.return_value = []
    convergence = {"min_total_score": 0.85, "min_dimension_score": 0.65, "max_iterations": 2}

    result = iterate(
        phase="phase1", module_name="_",
        generator=lambda i: "o",
        baseline_a={}, convergence=convergence,
        skill_dir=str(tmp_path / "skills"),
        snapshot_root=str(tmp_path / "snap"),
        iter_root=str(tmp_path / "iters"),
        abstraction_map={},
        max_revise_attempts=2,
    )
    assert result["converged"] is False
    assert result["iterations"] == 2
    assert "weak_dimensions" in result


@patch('phase_loop.is_converged', side_effect=[False, True])
@patch('phase_loop.run_analysis_cycle')
@patch('phase_loop.score_artifact')
@patch('phase_loop.patcher')
def test_iterate_reuses_completed_iteration_without_rerunning(
    mock_patcher, mock_score, mock_analyze, mock_is_converged, tmp_path
):
    iter_root = tmp_path / "iters"
    iter1_dir = iter_root / "iter-1"
    iter1_dir.mkdir(parents=True, exist_ok=True)
    (iter1_dir / "ai-output.md").write_text("saved output", encoding="utf-8")
    saved_score = {
        "total_weighted_score": 0.60,
        "dimensions": {"a": {"score": 0.50}},
        "weak_dimensions": ["coverage"],
    }
    (iter1_dir / "score.json").write_text(
        json.dumps(saved_score, ensure_ascii=False), encoding="utf-8"
    )
    (iter1_dir / "progress.json").write_text(
        json.dumps(
            {
                "status": "completed",
                "iter": 1,
                "step": "apply",
                "score": saved_score,
                "patches_applied": 1,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    mock_score.return_value = {
        "total_weighted_score": 0.90,
        "dimensions": {"a": {"score": 0.70}},
        "weak_dimensions": [],
    }
    mock_analyze.return_value = {
        "verdict": "PASS",
        "patch": {"patches": [{"file": "skills/x.md", "diff": "d"}]},
    }
    mock_patcher.apply_patches.return_value = []
    convergence = {"min_total_score": 0.85, "min_dimension_score": 0.65, "max_iterations": 3}

    gen_iters = []

    def fake_generator(iter_num):
        gen_iters.append(iter_num)
        return f"ai output {iter_num}"

    result = iterate(
        phase="phase1", module_name="_",
        generator=fake_generator,
        baseline_a={}, convergence=convergence,
        skill_dir=str(tmp_path / "skills"),
        snapshot_root=str(tmp_path / "snap"),
        iter_root=str(iter_root),
        abstraction_map={},
        max_revise_attempts=2,
    )

    assert result["converged"] is True
    assert result["iterations"] == 2
    assert gen_iters == [2]
    assert mock_score.call_count == 1
    assert mock_analyze.call_count == 0
