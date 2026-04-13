import subprocess
import json
import re
from pathlib import Path


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
    cmd = [
        "claude", "-p",
        "--model", model,
        "--output-format", "text",
        "--max-turns", "1",
    ]

    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding='utf-8',
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"claude -p failed (code {result.returncode}): {result.stderr}"
        )

    response = result.stdout.strip()

    # 确保输出目录存在
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    # 写入响应到文件
    Path(output).write_text(response, encoding='utf-8')

    if parse_json:
        return extract_json(response)

    return response
