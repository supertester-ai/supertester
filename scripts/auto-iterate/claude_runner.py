import os
import subprocess
import shutil
import json
import re
import sys
from pathlib import Path


def _resolve_git_bash() -> str | None:
    """Windows 上探测 git-bash 路径，用于 CLAUDE_CODE_GIT_BASH_PATH。

    Returns: bash.exe 绝对路径，或 None (非 Windows / 未找到)
    """
    if sys.platform != "win32":
        return None

    # 1. 已存在环境变量则尊重
    existing = os.environ.get("CLAUDE_CODE_GIT_BASH_PATH")
    if existing and Path(existing).exists():
        return existing

    # 2. 探测常见 git 安装路径 (排除 WSL/WindowsApps 的 bash)
    candidates = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        r"D:\Git\bin\bash.exe",
        r"D:\Program Files\Git\bin\bash.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c

    # 3. PATH 中查找 (过滤 WindowsApps / System32)
    bash_exe = shutil.which("bash")
    if bash_exe and "WindowsApps" not in bash_exe and "System32" not in bash_exe:
        return bash_exe

    return None


def _resolve_claude_executable() -> str:
    """跨平台解析 claude 可执行文件路径。

    Windows 上 claude 是 .cmd/.bat 包装器，subprocess 需要完整路径。
    """
    exe = shutil.which("claude")
    if exe is None:
        raise RuntimeError(
            "Could not find 'claude' executable in PATH. "
            "Ensure Claude Code CLI is installed."
        )
    return exe


_ANSI_RE = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')

# FCF Proxy / 类似包装器在输出开头打印的 box-drawing banner，需要跳过
_BANNER_BOX_RE = re.compile(
    r'^(\s*\+[-]+\+\s*\n(\s*\|[^\n]*\|\s*\n){1,5}\s*\+[-]+\+\s*\n)+',
    re.MULTILINE,
)


def _strip_ansi(text: str) -> str:
    """去除 ANSI 转义序列 (颜色码等)"""
    return _ANSI_RE.sub('', text)


def _strip_banner(text: str) -> str:
    """去除输出开头的 ASCII box banner (如 FCF Proxy banner)"""
    return _BANNER_BOX_RE.sub('', text, count=1)


def extract_json(text: str):
    """从文本中提取 JSON，支持裸 JSON 或 ```json ... ``` 包裹

    Args:
        text: 包含 JSON 的文本

    Returns:
        解析后的 JSON 对象，或 None 如果无法提取/解析
    """
    text = text.strip()

    # 尝试 ```json ... ``` fence (允许 fence 末尾无 newline)
    m = re.search(r'```(?:json)?\s*\n(.*?)\n?```', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试裸 JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 尝试找第一个 { 到最后一个 }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            return None

    return None


def _repair_json_via_claude(broken_text: str, output: str,
                            timeout: int = 120) -> dict | None:
    """当 extract_json 失败时，用 Claude 自动修复 JSON 转义问题。

    使用 haiku 模型（快且便宜），仅修复 JSON 格式，不改内容。
    """
    print("[claude_runner] JSON parse failed, attempting auto-repair via Claude...", flush=True)
    repair_prompt = (
        "The following text should be a single JSON object but json.loads() fails, "
        "most likely because some string field values contain unescaped ASCII double "
        "quotes or other characters that break JSON syntax.\n\n"
        "Your task: output ONLY the corrected JSON object. No fences, no preface, "
        "no trailing text. Preserve ALL original content and meaning — only fix "
        "JSON escaping (escape unescaped \" inside string values as \\\", etc).\n\n"
        "BROKEN TEXT:\n" + broken_text
    )
    try:
        raw = claude_call(
            repair_prompt, output + ".repair-raw",
            parse_json=False, model="haiku", timeout=timeout,
        )
        result = extract_json(raw)
        if result is not None:
            # 写出修复后的合法 JSON 方便调试
            Path(output).write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8'
            )
            print("[claude_runner] Auto-repair succeeded", flush=True)
        else:
            print("[claude_runner] Auto-repair failed — still cannot parse", flush=True)
        return result
    except Exception as e:
        print(f"[claude_runner] Auto-repair error: {e}", flush=True)
        return None


def claude_call(prompt: str, output: str, parse_json: bool = False,
                model: str = "sonnet", timeout: int = 300,
                max_turns: int = 30, max_retries: int = 2):
    """调用 claude -p，prompt 通过 stdin 传入，结果写入 output 文件。

    Args:
        prompt: 提示词内容
        output: 结果输出文件路径
        parse_json: 是否解析返回值为 JSON
        model: Claude 模型名
        timeout: 超时秒数
        max_retries: subprocess 调用失败后的重试次数（默认 2，共 3 次尝试）

    Returns:
        response 字符串，或 (parse_json=True 时) 解析后的对象，失败返回 None

    Raises:
        RuntimeError: 如果 claude 命令重试后仍返回非零退出码
    """
    claude_exe = _resolve_claude_executable()
    cmd = [
        claude_exe, "-p",
        "--model", model,
        "--output-format", "text",
        "--max-turns", str(max_turns),
    ]

    # Windows 上 Claude Code 需要 git-bash
    env = os.environ.copy()
    if sys.platform == "win32" and not env.get("CLAUDE_CODE_GIT_BASH_PATH"):
        bash_path = _resolve_git_bash()
        if bash_path:
            env["CLAUDE_CODE_GIT_BASH_PATH"] = bash_path

    last_err = None
    for attempt in range(1, max_retries + 2):
        try:
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace',
                env=env,
            )
            if result.returncode != 0:
                err_msg = result.stderr.strip() or "(empty stderr)"
                raise RuntimeError(
                    f"claude -p failed (code {result.returncode}): {err_msg}"
                )
            break  # 成功
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            last_err = e
            if attempt <= max_retries:
                print(f"[claude_runner] attempt {attempt}/{max_retries + 1} failed: {e}", flush=True)
                print(f"[claude_runner] retrying...", flush=True)
                continue
            # 重试耗尽，向上抛
            raise RuntimeError(
                f"claude -p failed after {max_retries + 1} attempts: {last_err}"
            ) from last_err

    response = _strip_banner(_strip_ansi(result.stdout)).strip()

    # 确保输出目录存在
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    # 写入响应到文件
    Path(output).write_text(response, encoding='utf-8')

    if parse_json:
        parsed = extract_json(response)
        if parsed is not None:
            return parsed
        # 自动修复：用 Claude haiku 修复转义问题
        return _repair_json_via_claude(response, output, timeout=min(timeout, 120))

    return response
