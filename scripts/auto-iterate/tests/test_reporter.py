from pathlib import Path
from reporter import generate_report
from state import State


def test_generate_report_creates_markdown(tmp_path):
    s = State(state_file=str(tmp_path / "s.json"))
    s.phase1_converged = True
    s.phase1_iterations = 2
    s.phase1_final_score = {"total_weighted_score": 0.83}
    s.phase2_converged = True
    s.phase2_iterations = 1
    s.phase2_final_score = {"total_weighted_score": 0.78}
    s.converged_modules = ["URL通用校验"]
    s.unconverged_modules = [{"module": "AI语义", "best_score": 0.72, "gap_dimensions": ["content_fidelity"]}]
    s.add_history("phase1", {"iter": 1, "score": 0.65})
    s.add_history("phase1", {"iter": 2, "score": 0.83})
    s.add_history("URL通用校验", {"iter": 1, "score": 0.88})

    report_path = tmp_path / "report.md"
    generate_report(s, str(report_path))

    text = report_path.read_text(encoding='utf-8')
    assert "URL通用校验" in text
    assert "AI语义" in text
    assert "0.83" in text
    assert "收敛" in text or "Converged" in text
