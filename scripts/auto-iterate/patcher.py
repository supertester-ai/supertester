import shutil
from pathlib import Path
from unidiff import PatchSet


def snapshot(src_dir: str, dst_dir: str):
    """整目录快照，dst 若存在则覆盖"""
    dst = Path(dst_dir)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src_dir, dst_dir)


def rollback(src_dir: str, snapshot_dir: str):
    """从快照恢复到 src_dir"""
    src = Path(src_dir)
    if src.exists():
        shutil.rmtree(src)
    shutil.copytree(snapshot_dir, src_dir)


def apply_patch(target_file: str, diff_text: str):
    """应用 unified diff 到单个文件。

    Args:
        target_file: 被补丁的文件绝对路径
        diff_text: unified diff 内容 (含 --- / +++ / @@ 头)
    """
    patch = PatchSet(diff_text)
    if len(patch) == 0:
        raise ValueError("Empty patch")

    patched_file = patch[0]
    original = Path(target_file).read_text(encoding='utf-8').splitlines(keepends=True)

    # 手动应用 hunks (unidiff 不提供 apply)
    result_lines = []
    src_line = 0  # 0-indexed position in original

    for hunk in patched_file:
        # hunk.source_start is 1-indexed
        hunk_start = hunk.source_start - 1
        # 先复制 hunk 前的未修改行
        while src_line < hunk_start:
            result_lines.append(original[src_line])
            src_line += 1
        # 处理 hunk 内每行
        for line in hunk:
            if line.is_context:
                result_lines.append(original[src_line])
                src_line += 1
            elif line.is_removed:
                src_line += 1  # 跳过原文件中这行
            elif line.is_added:
                value = line.value
                if not value.endswith('\n'):
                    value += '\n'
                result_lines.append(value)
    # 复制剩余行
    while src_line < len(original):
        result_lines.append(original[src_line])
        src_line += 1

    Path(target_file).write_text(''.join(result_lines), encoding='utf-8')


def apply_patches(patches: list, base_dir: str):
    """批量应用 patches。

    patches: [{"file": "relative/path.md", "diff": "..."}, ...]
    base_dir: patches 中 file 路径的根目录

    Returns: list of errors [{"file": ..., "error": ...}]
    """
    errors = []
    for p in patches:
        try:
            target = str(Path(base_dir) / p["file"])
            apply_patch(target, p["diff"])
        except Exception as e:
            errors.append({"file": p["file"], "error": str(e)})
    return errors
