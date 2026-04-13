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

    # 尝试 ```json ... ``` fence
    m = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
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


def claude_call(prompt: str, output: str, parse_json: bool = False,
                model: str = "sonnet", timeout: int = 300):
    """调用 claude -p，prompt 通过 stdin 传入，结果写入 output 文件。

    Args:
        prompt: 提示词内容
        output: 结果输出文件路径
        parse_json: 是否解析返回值为 JSON
        model: Claude 模型名
        timeout: 超时秒数

    Returns:
        response 字符串，或 (parse_json=True 时) 解析后的对象，失败返回 None

    Raises:
        RuntimeError: 如果 claude 命令返回非零退出码
    """
    claude_exe = _resolve_claude_executable()
    cmd = [
        claude_exe, "-p",
        "--model", model,
        "--output-format", "text",
        "--max-turns", "1",
    ]

    # Windows 上 Claude Code 需要 git-bash
    env = os.environ.copy()
    if sys.platform == "win32" and not env.get("CLAUDE_CODE_GIT_BASH_PATH"):
        bash_path = _resolve_git_bash()
        if bash_path:
            env["CLAUDE_CODE_GIT_BASH_PATH"] = bash_path

    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding='utf-8',
        env=env,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"claude -p failed (code {result.returncode}): {result.stderr}"
        )

    response = _strip_banner(_strip_ansi(result.stdout)).strip()

    # 确保输出目录存在
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    # 写入响应到文件
    Path(output).write_text(response, encoding='utf-8')

    if parse_json:
        return extract_json(response)

    return response
