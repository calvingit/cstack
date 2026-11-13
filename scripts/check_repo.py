#!/usr/bin/env python3
"""Lightweight checks for skill layout, names, links, and trigger policy.

The repository ships more than one plugin under ``plugins/``. Each plugin owns a
``.claude-plugin/plugin.json``, a version declared in both that manifest and the
root ``.claude-plugin/marketplace.json``, and its own skill prefix (``cstack-``
for ``plugins/cstack``, ``gitlab-`` for ``plugins/gitlab``). Every rule below is
applied per plugin.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS_ROOT = ROOT / "plugins"

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"```.*?```", re.S)
EXPLICIT_PHRASES = ("仅当用户手动触发",)
FORBIDDEN_MARKERS = ("不", "勿")
ALLOWED_DESCRIPTION_TOKENS = (
    "PR",
    "MR",
    "Seam",
    "API",
    "ID",
    "IID",
    "Agent",
    "Skill",
    "R#",
    "AC#",
    "diff",
    "GitLab",
    "glab",
    "CLI",
    "CI",
    "JSON",
    "YAML",
    "REST",
    "URL",
    "SHA",
    "HTTP",
    "SQL",
    "MCP",
    "LLM",
    "release",
)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.plugin_count = 0
        self.skill_count = 0

    def add(self, message: str) -> None:
        self.errors.append(message)


class Plugin:
    """One plugin directory under ``plugins/`` and its naming contract."""

    def __init__(self, root: Path, name: str, prefix: str) -> None:
        self.root = root
        self.name = name
        self.prefix = prefix
        self.core_skill = f"{prefix}core"

    @property
    def manifest_path(self) -> Path:
        return self.root / ".claude-plugin" / "plugin.json"

    @property
    def skills_root(self) -> Path:
        return self.root / "skills"

    @property
    def agents_root(self) -> Path:
        return self.root / "agents"

    def skill_dirs(self) -> list[Path]:
        if not self.skills_root.is_dir():
            return []
        return sorted(path for path in self.skills_root.iterdir() if path.is_dir())


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


def discover_plugins(report: Report) -> list[Plugin]:
    """Every plugin directory must declare itself via its own plugin.json."""
    if not PLUGINS_ROOT.is_dir():
        report.add(f"{rel(PLUGINS_ROOT)}: 目录不存在")
        return []
    plugins: list[Plugin] = []
    for directory in sorted(path for path in PLUGINS_ROOT.iterdir() if path.is_dir()):
        manifest = directory / ".claude-plugin" / "plugin.json"
        if not manifest.is_file():
            report.add(f"{rel(directory)}: 缺少 .claude-plugin/plugin.json")
            continue
        data = load_json(manifest, report)
        if not data:
            continue
        name = data.get("name")
        if not isinstance(name, str) or not name:
            report.add(f"{rel(manifest)}: 缺少 name")
            continue
        if name != directory.name:
            report.add(f"{rel(manifest)}: name {name!r} 与目录 {directory.name!r} 不一致")
        plugins.append(Plugin(directory, name, f"{name}-"))
    if not plugins:
        report.add(f"{rel(PLUGINS_ROOT)}: 没有可用的插件")
    return plugins


def check_marketplace_sources(plugins: list[Plugin], report: Report) -> dict | None:
    market_path = ROOT / ".claude-plugin" / "marketplace.json"
    market = load_json(market_path, report)
    if not market:
        return None
    entries = market.get("plugins") or []
    if not isinstance(entries, list) or not entries:
        report.add(f"{rel(market_path)}: plugins 为空")
        return market
    declared: dict[str, dict] = {}
    for item in entries:
        if not isinstance(item, dict):
            report.add(f"{rel(market_path)}: 插件条目不是对象")
            continue
        source = item.get("source")
        name = item.get("name", "<未命名>")
        if not isinstance(name, str):
            report.add(f"{rel(market_path)}: 插件 name 必须是字符串")
            continue
        if name in declared:
            report.add(f"{rel(market_path)}: 插件 {name} 重复声明")
        declared[name] = item
        if not isinstance(source, str):
            report.add(f"{rel(market_path)}: 插件 {name} 的 source 必须是相对路径字符串")
            continue
        relative = source[2:] if source.startswith("./") else source
        parts = Path(relative).parts
        if not relative or relative == "." or ".." in parts or Path(relative).is_absolute():
            report.add(
                f"{rel(market_path)}: 插件 {name} 的 source {source!r} 不能是仓库根或越出仓库"
            )
            continue
        resolved = (ROOT / relative).resolve()
        if (
            resolved == ROOT.resolve()
            or ROOT.resolve() not in resolved.parents
            or not resolved.is_dir()
        ):
            report.add(f"{rel(market_path)}: 插件 {name} 的 source {source!r} 不是仓库内目录")
            continue
        expected = f"plugins/{name}"
        if relative != expected:
            report.add(
                f"{rel(market_path)}: 插件 {name} 的 source {source!r}，应为 './{expected}'"
            )
    for plugin in plugins:
        if plugin.name not in declared:
            report.add(f"{plugin.name}: 插件未在 marketplace.json 中声明")
    return market


def check_versions(plugins: list[Plugin], market: dict | None, report: Report) -> None:
    if market is None:
        return
    market_path = ROOT / ".claude-plugin" / "marketplace.json"
    entries = {item.get("name"): item for item in market.get("plugins") or [] if isinstance(item, dict)}
    for plugin in plugins:
        data = load_json(plugin.manifest_path, report)
        if not data:
            continue
        plugin_version = data.get("version")
        if not plugin_version:
            report.add(f"{rel(plugin.manifest_path)}: 缺少 version")
        entry = entries.get(plugin.name)
        if entry is None:
            continue
        entry_version = entry.get("version")
        if not entry_version:
            report.add(f"{rel(market_path)}: 插件 {plugin.name} 缺少 version")
        elif entry_version != plugin_version:
            report.add(
                f"版本不一致: {plugin.name} 的 plugin.json={plugin_version!r}，"
                f"marketplace.json={entry_version!r}"
            )


HOST_MANIFESTS = (
    ("plugin.json", "Agent Plugins"),
    (".codex-plugin/plugin.json", "Codex"),
    (".cursor-plugin/plugin.json", "Cursor"),
    (".github/plugin/plugin.json", "GitHub Copilot"),
    (".grok-plugin/plugin.json", "Grok"),
    ("gemini-extension.json", "Gemini CLI"),
    ("kimi.plugin.json", "Kimi Code"),
)


def check_host_manifests(plugin: Plugin, report: Report) -> None:
    """Each supported host manifest must agree on plugin name and version."""
    canonical = load_json(plugin.manifest_path, report)
    if not canonical:
        return
    name = canonical.get("name")
    version = canonical.get("version")
    for relative, host in HOST_MANIFESTS:
        path = plugin.root / relative
        if not path.is_file():
            report.add(f"{rel(path)}: 缺少 {host} 清单")
            continue
        data = load_json(path, report)
        if not data:
            continue
        if data.get("name") != name:
            report.add(
                f"{rel(path)}: name {data.get('name')!r} 与 {rel(plugin.manifest_path)} 的 {name!r} 不一致"
            )
        if data.get("version") != version:
            report.add(
                f"{rel(path)}: version {data.get('version')!r} 与 {rel(plugin.manifest_path)} 的 {version!r} 不一致"
            )


def check_agents_marketplace(plugins: list[Plugin], report: Report) -> None:
    """The Codex repo marketplace must expose every plugin with its version."""
    path = ROOT / ".agents" / "plugins" / "marketplace.json"
    if not path.is_file():
        report.add(f"{rel(path)}: 缺少 Codex 市场文件")
        return
    data = load_json(path, report)
    if not data:
        return
    entries = {
        item.get("name"): item
        for item in data.get("plugins") or []
        if isinstance(item, dict)
    }
    for plugin in plugins:
        canonical = load_json(plugin.manifest_path, report)
        if not canonical:
            continue
        entry = entries.get(plugin.name)
        if entry is None:
            report.add(f"{rel(path)}: 缺少插件 {plugin.name} 的条目")
            continue
        if entry.get("version") != canonical.get("version"):
            report.add(
                f"{rel(path)}: {plugin.name} 的 version={entry.get('version')!r}，"
                f"与 {rel(plugin.manifest_path)} 的 {canonical.get('version')!r} 不一致"
            )
        source = entry.get("source")
        if not isinstance(source, dict) or source.get("source") != "local":
            report.add(
                f"{rel(path)}: {plugin.name} 的 source 必须是 local 来源对象"
            )
            continue
        expected_path = f"./plugins/{plugin.name}"
        if source.get("path") != expected_path:
            report.add(
                f"{rel(path)}: {plugin.name} 的 source.path={source.get('path')!r}，应为 {expected_path!r}"
            )


def check_grok_marketplace(plugins: list[Plugin], report: Report) -> None:
    """The Grok marketplace must expose every plugin with its manifest version."""
    path = ROOT / ".grok-plugin" / "marketplace.json"
    if not path.is_file():
        report.add(f"{rel(path)}: 缺少 Grok 市场文件")
        return
    data = load_json(path, report)
    if not data:
        return
    entries = {
        item.get("name"): item
        for item in data.get("plugins") or []
        if isinstance(item, dict)
    }
    for plugin in plugins:
        canonical = load_json(plugin.manifest_path, report)
        if not canonical:
            continue
        entry = entries.get(plugin.name)
        if entry is None:
            report.add(f"{rel(path)}: 缺少插件 {plugin.name} 的条目")
            continue
        if entry.get("version") != canonical.get("version"):
            report.add(
                f"{rel(path)}: {plugin.name} 的 version={entry.get('version')!r}，"
                f"与 {rel(plugin.manifest_path)} 的 {canonical.get('version')!r} 不一致"
            )
        expected_source = f"./plugins/{plugin.name}"
        if entry.get("source") != expected_source:
            report.add(
                f"{rel(path)}: {plugin.name} 的 source={entry.get('source')!r}，应为 {expected_source!r}"
            )


def check_skill(directory: Path, plugin: Plugin, report: Report) -> None:
    report.skill_count += 1
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
    if not name or not name.startswith(plugin.prefix) or name.startswith(f"{plugin.prefix}{plugin.prefix}"):
        report.add(
            f"{rel(skill_md)}: name 必须使用 {plugin.prefix} 前缀，当前为 {name!r}"
        )
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
    if description and any(marker in description for marker in FORBIDDEN_MARKERS):
        report.add(
            f"{rel(skill_md)}: description 只写正向陈述，含否定表述: {description}"
        )
    core_invocation_phrase = f"调用 `{plugin.core_skill}`"
    if name != plugin.core_skill and core_invocation_phrase in text:
        report.add(
            f"{rel(skill_md)}: 共享层是文件索引，应写成读取文件，不写成「调用 Skill」"
        )

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
        report.add(f"{rel(skill_md)}: 描述要求手动触发，但未设置 disable-model-invocation: true")
    if explicit_by_text and allow is not False:
        report.add(f"{rel(skill_md)}: 描述要求手动触发，但 Codex 未关闭隐式调用")
    if description and not explicit_by_text and disabled:
        report.add(f"{rel(skill_md)}: 描述像可自动触发，但设置了 disable-model-invocation: true")
    if description and not explicit_by_text and allow is False:
        report.add(f"{rel(skill_md)}: 描述像可自动触发，但 Codex allow_implicit_invocation 为 false")


def check_agents(plugin: Plugin, report: Report) -> None:
    files = sorted(path for path in plugin.agents_root.glob("*.md") if path.is_file())
    if not files:
        report.add(f"{rel(plugin.agents_root)}: 没有子代理定义")
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
        if not name or not name.startswith(plugin.prefix):
            report.add(f"{rel(path)}: 子代理 name 必须使用 {plugin.prefix} 前缀")
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
    plugins = discover_plugins(report)
    market = check_marketplace_sources(plugins, report)
    for plugin in plugins:
        skill_dirs = plugin.skill_dirs()
        if not skill_dirs:
            report.add(f"{rel(plugin.skills_root)}: 没有 Skill 目录")
        for directory in skill_dirs:
            check_skill(directory, plugin, report)
        check_agents(plugin, report)
        check_host_manifests(plugin, report)
    check_versions(plugins, market, report)
    check_agents_marketplace(plugins, report)
    check_grok_marketplace(plugins, report)
    check_links(report)
    check_licenses(report)
    report.plugin_count = len(plugins)
    if report.errors:
        print(f"检查失败，共 {len(report.errors)} 项：", file=sys.stderr)
        for error in report.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"检查通过：{report.plugin_count} 个插件、{report.skill_count} 个 Skill，"
        "版本、触发策略、前缀、链接和许可文件均一致。"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
