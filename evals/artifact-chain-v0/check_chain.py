#!/usr/bin/env python3
"""检查 CStack 产物链的引用是否闭合。

只校验语义关系，不规定文本格式：真实产物可以是会话、Markdown、issue 或 PR 描述。
sample.json 的字段结构只是为了让检查可自动运行，不是要求产物长成 JSON。
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def check_cycles(edges):
    """edges: {s: [blocked_by...]}；返回环上的节点列表。"""
    state = {}
    stack = []
    cycles = []

    def visit(node):
        if state.get(node) == 1:
            i = stack.index(node)
            cycles.extend(stack[i:])
            return
        if state.get(node) == 2:
            return
        state[node] = 1
        stack.append(node)
        for nxt in edges.get(node, []):
            visit(nxt)
        stack.pop()
        state[node] = 2

    for node in edges:
        visit(node)
    return sorted(set(cycles))


def main(path):
    data = load(path)
    errors = []
    warnings = []

    decisions = data.get("decisions", [])
    spec = data.get("spec", {})
    tech = data.get("tech", {})
    slices = data.get("slices", [])
    evidence = data.get("evidence", {})

    # --- DECISIONS ---
    decision_by_id = {}
    for d in decisions:
        did = d.get("id")
        if not did:
            errors.append("DECISIONS 存在缺少 id 的条目")
            continue
        if did in decision_by_id:
            errors.append(f"DECISIONS 重复 id: {did}")
        decision_by_id[did] = d

    # --- SPEC: requirements ---
    requirements = spec.get("requirements", [])
    req_by_id = {}
    for r in requirements:
        rid = r.get("id")
        if not rid:
            errors.append("SPEC 存在缺少 id 的 requirement")
            continue
        if rid in req_by_id:
            errors.append(f"SPEC 重复 requirement id: {rid}")
        req_by_id[rid] = r
        src = r.get("source")
        if src and src not in decision_by_id:
            errors.append(f"{rid} 的来源 {src} 不在 DECISIONS 中")
        if src and decision_by_id.get(src, {}).get("status") != "confirmed":
            errors.append(f"{rid} 引用了未确认的 {src}")

    # --- SPEC: acceptance ---
    acceptance = spec.get("acceptance", [])
    ac_by_id = {}
    for a in acceptance:
        aid = a.get("id")
        if not aid:
            errors.append("SPEC 存在缺少 id 的 AC")
            continue
        if aid in ac_by_id:
            errors.append(f"SPEC 重复 AC id: {aid}")
        ac_by_id[aid] = a
        if a.get("source") not in req_by_id:
            errors.append(f"{aid} 的来源 {a.get('source')} 不在 R 中")
        if not a.get("criterion") or not a.get("observable"):
            errors.append(f"{aid} 缺少 criterion 或 observable")

    for r in requirements:
        if not any(a.get("source") == r.get("id") for a in acceptance):
            errors.append(f"{r.get('id')} 没有 AC 覆盖")

    open_decisions = {d["id"] for d in decisions if d.get("status") == "open"}
    for did in open_decisions:
        if did not in set(spec.get("open", [])):
            warnings.append(f"未决 {did} 未在 SPEC.open 中保留，避免静默假设")

    # --- TECH ---
    design_by_id = {}
    for d in tech.get("decisions", []):
        did = d.get("id")
        if not did:
            errors.append("TECH 存在缺少 id 的 D")
            continue
        if did in design_by_id:
            errors.append(f"TECH 重复 D id: {did}")
        design_by_id[did] = d
        basis = d.get("basis") or []
        if not basis:
            errors.append(f"{did} 没有依据（R/AC 或代码事实）")
        for item in basis:
            if item in req_by_id or item in ac_by_id:
                continue
            if isinstance(item, str) and item.startswith("code:"):
                continue
            errors.append(f"{did} 的依据 {item!r} 既不是 R/AC，也不是 code: 事实")

    # --- SLICES ---
    slice_by_id = {}
    edges = {}
    local_ac_owner = {}
    for s in slices:
        sid = s.get("id")
        if not sid:
            errors.append("SLICES 存在缺少 id 的切片")
            continue
        if sid in slice_by_id:
            errors.append(f"SLICES 重复 S id: {sid}")
        slice_by_id[sid] = s
        if not s.get("delivers"):
            errors.append(f"{sid} 缺少 delivers")
        covers = s.get("covers") or {}
        refs = {
            "requirements": req_by_id,
            "acceptance": ac_by_id,
            "design": design_by_id,
        }
        covered = 0
        for key, pool in refs.items():
            for ref in covers.get(key) or []:
                if ref not in pool:
                    errors.append(f"{sid} 的 covers.{key} 引用了不存在的 {ref}")
                else:
                    covered += 1
        if covered == 0:
            errors.append(f"{sid} 没有覆盖任何 R/AC/D")
        if covers.get("design") and not design_by_id:
            errors.append(f"{sid} 引用了 D，但 TECH 为空")
        for lac in s.get("local_ac") or []:
            if lac in local_ac_owner:
                errors.append(f"切片本地 AC 重复: {lac}")
            local_ac_owner[lac] = sid
        edges[sid] = list(s.get("blocked_by") or [])

    for sid, blockers in edges.items():
        for b in blockers:
            if b not in slice_by_id:
                errors.append(f"{sid} 的 blocked_by 引用了不存在的 {b}")
            if b == sid:
                errors.append(f"{sid} 不能阻塞自己")

    for node in check_cycles(edges):
        errors.append(f"SLICES 依赖成环: {node}")

    if slices:
        for aid in ac_by_id:
            if not any(aid in (s.get("covers", {}).get("acceptance") or []) for s in slices):
                warnings.append(f"AC {aid} 没有落在任何切片上")

    # --- EVIDENCE ---
    results = evidence.get("results", [])
    seen = set()
    for res in results:
        aid = res.get("ac")
        if aid not in ac_by_id:
            errors.append(f"EVIDENCE 引用了不存在的 AC: {aid}")
        if aid in seen:
            errors.append(f"EVIDENCE 对 {aid} 有多条结论")
        seen.add(aid)
        sid = res.get("slice")
        if sid and sid not in slice_by_id:
            errors.append(f"EVIDENCE 引用了不存在的切片: {sid}")
        verdict = res.get("verdict")
        if verdict not in {"PASS", "FAIL", "NOT VERIFIED"}:
            errors.append(f"{aid} 的 verdict 非法: {verdict}")
        if verdict == "PASS":
            for field in ("method", "environment", "executor"):
                if not res.get(field):
                    errors.append(f"{aid} 标 PASS 但缺少 {field}")

    for aid in ac_by_id:
        if aid not in seen:
            errors.append(f"AC {aid} 没有任何 EVIDENCE 结论")

    if not (evidence.get("candidate") or {}).get("head"):
        errors.append("EVIDENCE 缺少候选 HEAD")

    print("== CStack 产物链检查 ==")
    print(
        "决定 {}（未决 {}）｜ 需求 {}｜ 验收 {}｜ 技术决定 {}｜ 切片 {}｜ 证据 {}".format(
            len(decision_by_id),
            len(open_decisions),
            len(req_by_id),
            len(ac_by_id),
            len(design_by_id),
            len(slice_by_id),
            len(results),
        )
    )
    for w in warnings:
        print("WARN:", w)
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1
    print("结果: 通过（引用闭合，依赖无环，未决项保留）")
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "sample.json")
    raise SystemExit(main(target))
