from pathlib import Path
from patcher import snapshot, rollback, apply_patch


def test_snapshot_copies_directory(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.md").write_text("hello", encoding='utf-8')
    (src / "sub").mkdir()
    (src / "sub" / "b.md").write_text("world", encoding='utf-8')

    snap = tmp_path / "snap"
    snapshot(str(src), str(snap))

    assert (snap / "a.md").read_text(encoding='utf-8') == "hello"
    assert (snap / "sub" / "b.md").read_text(encoding='utf-8') == "world"


def test_rollback_restores_content(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.md").write_text("original", encoding='utf-8')

    snap = tmp_path / "snap"
    snapshot(str(src), str(snap))

    (src / "a.md").write_text("modified", encoding='utf-8')
    assert (src / "a.md").read_text(encoding='utf-8') == "modified"

    rollback(str(src), str(snap))
    assert (src / "a.md").read_text(encoding='utf-8') == "original"


def test_apply_patch_unified_diff(tmp_path):
    target = tmp_path / "a.md"
    target.write_text("line 1\nline 2\nline 3\n", encoding='utf-8')

    diff = """--- a/a.md
+++ b/a.md
@@ -1,3 +1,3 @@
 line 1
-line 2
+line 2 modified
 line 3
"""
    apply_patch(str(target), diff)
    content = target.read_text(encoding='utf-8')
    assert "line 2 modified" in content
    assert "line 1" in content
    assert "line 3" in content
