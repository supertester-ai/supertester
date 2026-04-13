from unittest.mock import patch
from analyzer import generate_patch, review_patch, revise_patch, run_analysis_cycle


@patch('analyzer.claude_call')
def test_generate_patch_calls_claude(mock_call, tmp_path):
    mock_call.return_value = {
        "analysis": [],
        "patches": [{"file": "skills/x.md", "diff": "--- a\n+++ b\n"}],
        "skipped_gaps": [],
    }
    result = generate_patch(
        score={"total_weighted_score": 0.70},
        skill_content="skill text",
        iteration_history=[],
        abstraction_map={},
        output_path=str(tmp_path / "p.json"),
    )
    assert "patches" in result
    mock_call.assert_called_once()


@patch('analyzer.claude_call')
def test_review_patch_returns_pass(mock_call, tmp_path):
    mock_call.return_value = {"verdict": "PASS", "issues": []}
    result = review_patch(
        patch={"patches": []}, skill_content="",
        output_path=str(tmp_path / "r.json"),
    )
    assert result["verdict"] == "PASS"


@patch('analyzer.revise_patch')
@patch('analyzer.review_patch')
@patch('analyzer.generate_patch')
def test_run_analysis_cycle_pass_first_try(mock_gen, mock_review, mock_revise, tmp_path):
    mock_gen.return_value = {"patches": [{"file": "x", "diff": "d"}]}
    mock_review.return_value = {"verdict": "PASS", "issues": []}

    result = run_analysis_cycle(
        score={}, skill_content="", iteration_history=[],
        abstraction_map={}, iter_dir=str(tmp_path),
        max_revise_attempts=2,
    )
    assert result["verdict"] == "PASS"
    assert result["patch"] == mock_gen.return_value
    mock_revise.assert_not_called()


@patch('analyzer.revise_patch')
@patch('analyzer.review_patch')
@patch('analyzer.generate_patch')
def test_run_analysis_cycle_revise_then_pass(mock_gen, mock_review, mock_revise, tmp_path):
    mock_gen.return_value = {"patches": [{"file": "x", "diff": "d"}]}
    mock_review.side_effect = [
        {"verdict": "REVISE", "issues": [{"problem": "GEO leaks"}]},
        {"verdict": "PASS", "issues": []},
    ]
    mock_revise.return_value = {"patches": [{"file": "x", "diff": "d2"}]}

    result = run_analysis_cycle(
        score={}, skill_content="", iteration_history=[],
        abstraction_map={}, iter_dir=str(tmp_path),
        max_revise_attempts=2,
    )
    assert result["verdict"] == "PASS"
    assert result["patch"] == mock_revise.return_value


@patch('analyzer.revise_patch')
@patch('analyzer.review_patch')
@patch('analyzer.generate_patch')
def test_run_analysis_cycle_exhausts_revise_attempts(mock_gen, mock_review, mock_revise, tmp_path):
    mock_gen.return_value = {"patches": [{"file": "x", "diff": "d"}]}
    mock_review.return_value = {"verdict": "REVISE", "issues": [{"problem": "x"}]}
    mock_revise.return_value = {"patches": [{"file": "x", "diff": "d2"}]}

    result = run_analysis_cycle(
        score={}, skill_content="", iteration_history=[],
        abstraction_map={}, iter_dir=str(tmp_path),
        max_revise_attempts=2,
    )
    # max_revise_attempts=2 → 3 reviews total, all REVISE
    assert result["verdict"] == "REVISE"
    assert result.get("skip_apply") is True
