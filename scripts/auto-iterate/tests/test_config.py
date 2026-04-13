from config import Config


def test_config_defaults():
    cfg = Config()
    assert cfg.prd_path.endswith("VisiGEO-PRD.md")
    assert cfg.reference_path.endswith(".json")
    assert cfg.model == "sonnet"
    assert cfg.convergence["phase3"]["min_total_score"] == 0.85
    assert "process_feedback" in " ".join(cfg.abstraction_map.values())


def test_config_convergence_structure():
    cfg = Config()
    for phase in ["phase1", "phase2", "phase3"]:
        assert "min_total_score" in cfg.convergence[phase]
        assert "min_dimension_score" in cfg.convergence[phase]
        assert "max_iterations" in cfg.convergence[phase]
