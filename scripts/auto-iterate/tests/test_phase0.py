from unittest.mock import patch, MagicMock
from pathlib import Path
import json
from phase0 import extract_baselines_for_module, merge_baselines


def test_merge_baselines_combines_module_results():
    m1 = {
        "module_name": "A",
        "phase1": {"content_assets": ["a1"]},
        "phase2": {},
        "phase3": {"checkpoints": [{"id": "BP-A-1"}]}
    }
    m2 = {
        "module_name": "B",
        "phase1": {"content_assets": ["b1"]},
        "phase2": {},
        "phase3": {"checkpoints": [{"id": "BP-B-1"}]}
    }
    merged = merge_baselines([m1, m2])

    assert "A" in merged["phase1"]
    assert "B" in merged["phase1"]
    assert merged["phase1"]["A"]["content_assets"] == ["a1"]
    assert len(merged["phase3"]["A"]["checkpoints"]) == 1


@patch('phase0.claude_call')
def test_extract_baselines_for_module_calls_claude(mock_call, tmp_path):
    mock_call.return_value = {
        "module_name": "URL通用校验",
        "phase1": {"content_assets": []},
        "phase2": {},
        "phase3": {"checkpoints": []}
    }
    module = {
        "name": "URL通用校验",
        "prd_content": "some prd",
        "ref_cases": [{"case_id": "1", "steps": []}]
    }
    result = extract_baselines_for_module(
        module, str(tmp_path / "out.json"), model="sonnet"
    )
    assert result["module_name"] == "URL通用校验"
    mock_call.assert_called_once()
