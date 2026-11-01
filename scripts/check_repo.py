#!/usr/bin/env python3
"""Lightweight checks for CStack skill layout, names, links, and trigger policy."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"```.*?```", re.S)
EXPLICIT_PHRASES = ("仅当用户手动触发", "不自动触发")
EXCLUSION_MARKERS = ("不用于", "不判断", "不记录", "不决定", "不负责", "不要", "不做")
CORE_INVOCATION_PHRASE = "调用 `cstack-core`"
ALLOWED_DESCRIPTION_TOKENS = ("PR", "Seam", "API", "ID", "Agent", "Skill", "R#", "AC#", "diff")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def add(self, message: str) -> None:
        self.errors.append(message)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, text
    return text[4:end], text[end + 5 :]


def field(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.*)$", frontmatter, re.M)
    if not match:
        return None
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return value


def load_json(path: Path, report: Report) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.add(f"{rel(path)}: 无法读取 JSON ({exc})")
        return None


def check_versions(report: Report) -> None:
    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    market_path = ROOT / ".claude-plugin" / "marketplace.json"
    plugin = load_json(plugin_path, report)
    market = load_json(market_path, report)
    if not plugin or not market:
        return
    plugin_version = plugin.get("version")
    plugins = market.get("plugins") or []
    if not isinstance(plugins, list) or not plugins:
        report.add(f"{rel(market_path)}: plugins 为空")
        return
    versions = []
    for item in plugins:
        if not isinstance(item, dict) or "version" not in item:
            report.add(f"{rel(market_path)}: 有插件缺少 version")
            continue
        versions.append(item["version"])
    if not plugin_version:
        report.add(f"{rel(plugin_path)}: 缺少 version")
    for version in versions:
        if version != plugin_version:
            report.add(
                f"版本不一致: plugin.json={plugin_version!r}，marketplace.json={version!r}"
            )


def check_skill(directory: Path, report: Report) -> None:
    skill_md = directory / "SKILL.md"
    openai = directory / "agents" / "openai.yaml"
    if not skill_md.is_file():
        report.add(f"{rel(directory)}: 缺少 SKILL.md")
        return
    text = skill_md.read_text(encoding="utf-8")
    frontmatter, _body = split_frontmatter(text)
    if frontmatter is None:
        report.add(f"{rel(skill_md)}: 缺少 frontmatter")
        return
    name = field(frontmatter, "name")
    description = field(frontmatter, "description")
    if name != directory.name:
        report.add(f"{rel(skill_md)}: name {name!r} 与目录 {directory.name!r} 不一致")
    if not name or not name.startswith("cstack-") or name.startswith("cstack-cstack-"):
        report.add(f"{rel(skill_md)}: name 必须是 cstack- 前缀，当前为 {name!r}")
    if not description:
        report.add(f"{rel(skill_md)}: 缺少 description")
    else:
        # Trigger descriptions are Chinese-first; allow a small set of established terms.
        description_for_check = description
        for token in sorted(ALLOWED_DESCRIPTION_TOKENS, key=len, reverse=True):
            description_for_check = re.sub(
                rf"(?<![A-Za-z0-9_-]){re.escape(token)}(?![A-Za-z0-9_-])",
                "",
                description_for_check,
            )
        if re.search(r"[A-Za-z]", description_for_check):
            report.add(f"{rel(skill_md)}: description 含未列入白名单的英文字母: {description}")
        if "时使用" not in description:
            report.add(f"{rel(skill_md)}: description 不是触发语句（应包含「时使用」）")
    disable = field(frontmatter, "disable-model-invocation")
    explicit_by_text = bool(description) and any(phrase in description for phrase in EXPLICIT_PHRASES)
    disabled = disable == "true"
    if disable not in (None, "true", "false"):
        report.add(f"{rel(skill_md)}: disable-model-invocation 只能是 true 或 false")
    if description and not disabled:
        if not any(marker in description for marker in EXCLUSION_MARKERS):
            report.add(
                f"{rel(skill_md)}: 自动触发的 description 要写明排除条件（不用于 / 不判断 / 不决定 …）"
            )
    if name != "cstack-core" and CORE_INVOCATION_PHRASE in text:
        report.add(f"{rel(skill_md)}: 共享层是文件索引，应写成读取文件，不写成「调用 Skill」")

    if not openai.is_file():
        report.add(f"{rel(directory)}: 缺少 agents/openai.yaml")
        allow = None
        prompt = ""
    else:
        yaml_text = openai.read_text(encoding="utf-8")
        allow_match = re.search(r"^  allow_implicit_invocation:\s*(true|false)\s*$", yaml_text, re.M)
        prompt_match = re.search(r'^  default_prompt:\s*"(.*)"\s*$', yaml_text, re.M)
        display_match = re.search(r'^  display_name:\s*"(.*)"\s*$', yaml_text, re.M)
        if not allow_match:
            report.add(f"{rel(openai)}: 缺少 policy.allow_implicit_invocation")
            allow = None
        else:
            allow = allow_match.group(1) == "true"
        if not display_match or not display_match.group(1).strip():
            report.add(f"{rel(openai)}: 缺少 display_name")
        prompt = prompt_match.group(1) if prompt_match else ""
        if not prompt:
            report.add(f"{rel(openai)}: 缺少 default_prompt")
        elif name and f"${name}" not in prompt:
            report.add(f"{rel(openai)}: default_prompt 未使用 ${name}")

    if disable == "true" and allow is True:
        report.add(f"{rel(skill_md)}: Claude 禁用自动调用，但 Codex allow_implicit_invocation 为 true")
    if disable != "true" and allow is False:
        report.add(f"{rel(skill_md)}: Claude 允许自动调用，但 Codex allow_implicit_invocation 为 false")
    if explicit_by_text and not disabled:
        report.add(f"{rel(skill_md)}: 描述要求手动触发或不自动触发，但未设置 disable-model-invocation: true")
    if explicit_by_text and allow is not False:
        report.add(f"{rel(skill_md)}: 描述要求手动触发或不自动触发，但 Codex 未关闭隐式调用")
    if description and not explicit_by_text and disabled:
        report.add(f"{rel(skill_md)}: 描述像可自动触发，但设置了 disable-model-invocation: true")
    if description and not explicit_by_text and allow is False:
        report.add(f"{rel(skill_md)}: 描述像可自动触发，但 Codex allow_implicit_invocation 为 false")


def check_agents(report: Report) -> None:
    agents = ROOT / "agents"
    files = sorted(path for path in agents.glob("*.md") if path.is_file())
    if not files:
        report.add("agents/: 没有子代理定义")
    for path in files:
        text = path.read_text(encoding="utf-8")
        frontmatter, _body = split_frontmatter(text)
        if frontmatter is None:
            report.add(f"{rel(path)}: 缺少 frontmatter")
            continue
        name = field(frontmatter, "name")
        description = field(frontmatter, "description")
        if name != path.stem:
            report.add(f"{rel(path)}: name {name!r} 与文件名 {path.stem!r} 不一致")
        if not name or not name.startswith("cstack-"):
            report.add(f"{rel(path)}: 子代理 name 必须使用 cstack- 前缀")
        if not description:
            report.add(f"{rel(path)}: 缺少 description")


def check_links(report: Report) -> None:
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = FENCE_RE.sub("", path.read_text(encoding="utf-8"))
        for match in LINK_RE.finditer(text):
            raw = match.group(1).strip()
            if raw.startswith("<") and raw.endswith(">"):
                raw = raw[1:-1]
            target = raw.split()[0] if raw else ""
            target = target.split("#", 1)[0]
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                report.add(f"{rel(path)}: 失效链接 {raw}")


def check_licenses(report: Report) -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if re.search(r"LICENSE|ATTRIBUTION|ATTRIBUTES", path.name, re.I):
            report.add(f"应删除的许可或署名文件: {rel(path)}")


def main() -> int:
    report = Report()
    skills_root = ROOT / "skills"
    skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
    if not skill_dirs:
        report.add("skills/: 没有 Skill 目录")
    for directory in skill_dirs:
        check_skill(directory, report)
    check_agents(report)
    check_versions(report)
    check_links(report)
    check_licenses(report)
    if report.errors:
        print(f"检查失败，共 {len(report.errors)} 项：", file=sys.stderr)
        for error in report.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"检查通过：{len(skill_dirs)} 个 Skill，版本、触发策略、前缀、链接和许可文件均一致。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
