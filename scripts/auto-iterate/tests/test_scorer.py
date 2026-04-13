from unittest.mock import patch
from pathlib import Path
import json
from scorer import is_converged, score_artifact


def test_is_converged_true():
    """检查评分满足收敛条件时返回 True"""
    score = {
        "total_weighted_score": 0.86,
        "dimensions": {
            "a": {"score": 0.70},
            "b": {"score": 0.80},
        },
    }
    cfg = {"min_total_score": 0.85, "min_dimension_score": 0.65}
    assert is_converged(score, cfg) is True


def test_is_converged_fails_dimension_floor():
    """检查某个维度未达到最低分时返回 False"""
    score = {
        "total_weighted_score": 0.86,
        "dimensions": {
            "a": {"score": 0.50},
            "b": {"score": 0.80},
        },
    }
    cfg = {"min_total_score": 0.85, "min_dimension_score": 0.65}
    assert is_converged(score, cfg) is False


def test_is_converged_fails_total():
    """检查总分未达到最低分时返回 False"""
    score = {
        "total_weighted_score": 0.80,
        "dimensions": {
            "a": {"score": 0.70},
            "b": {"score": 0.80},
        },
    }
    cfg = {"min_total_score": 0.85, "min_dimension_score": 0.65}
    assert is_converged(score, cfg) is False


@patch('scorer.claude_call')
def test_score_artifact_calls_claude_with_rendered_prompt(mock_call, tmp_path):
    """检查 score_artifact 调用 claude_call 并返回结果"""
    mock_call.return_value = {
        "total_weighted_score": 0.88,
        "dimensions": {},
        "converged": True,
    }
    result = score_artifact(
        phase="phase3",
        module_name="URL",
        iteration=1,
        ai_output="cases here",
        baseline_a={"checkpoints": []},
        output_path=str(tmp_path / "score.json"),
        convergence={"min_total_score": 0.85, "min_dimension_score": 0.65},
    )
    assert result["total_weighted_score"] == 0.88
    assert result["converged"] is True
    mock_call.assert_called_once()
