from unittest.mock import patch
from generators import make_phase1_generator, make_phase3_generator

@patch('generators.claude_call')
def test_phase1_generator_renders_prompt(mock_call, tmp_path):
    mock_call.return_value = "parsed output"
    (tmp_path / "skills" / "requirement-analysis").mkdir(parents=True)
    (tmp_path / "skills" / "requirement-analysis" / "SKILL.md").write_text("skill text", encoding='utf-8')

    gen = make_phase1_generator(
        prd_content="prd text",
        skill_dir=str(tmp_path / "skills"),
        output_root=str(tmp_path / "iters"),
    )
    result = gen(1)
    assert result == "parsed output"
    mock_call.assert_called_once()
    # check prompt was rendered with both prd and skill
    call_args = mock_call.call_args[0]
    assert "prd text" in call_args[0]
    assert "skill text" in call_args[0]

@patch('generators.claude_call')
def test_phase3_generator_includes_module_context(mock_call, tmp_path):
    mock_call.return_value = "tc text"
    (tmp_path / "skills" / "test-case-generation").mkdir(parents=True)
    (tmp_path / "skills" / "test-case-generation" / "SKILL.md").write_text("gen skill", encoding='utf-8')
    (tmp_path / "skills" / "test-case-generation" / "generator-reference.md").write_text("gen ref", encoding='utf-8')

    gen = make_phase3_generator(
        module_name="URL通用校验", module_prd="prd slice",
        parsed_requirements="parsed content",
        associations="assoc content",
        skill_dir=str(tmp_path / "skills"),
        output_root=str(tmp_path / "iters"),
    )
    result = gen(1)
    assert result == "tc text"
    prompt = mock_call.call_args[0][0]
    assert "URL通用校验" in prompt
    assert "prd slice" in prompt
    assert "gen ref" in prompt
