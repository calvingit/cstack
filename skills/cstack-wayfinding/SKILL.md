---
name: cstack-wayfinding
description: 当一大块工作超出单个会话、方向还看不清，需要跨会话用一张地图和决策票据推进时使用。已经清楚的小改动不要用。
---

# Wayfinding - 跨会话找路

## 底线（独立安装时自足）

- 规划，不直接做：每张决策票据解决一个决策；地图在通往目的地的路清楚时结束。
- 不在地图外偷偷扩范围；超出目的地的是 Out of scope，不是迷雾。
- 一次会话最多解决一个决策票据；research 票据可以并行。
- 地图与票据是共享记录，不是新的运行状态机。

## 产物

- **读**：松散想法、项目现状、已有文档与 ADR。
- **写**：MAP（Destination、Notes、Decisions so far、Not yet specified、Out of scope）和决策票据（Question、类型、blocked-by）。放在项目已有的任务或 tracker 形式；不建第二套状态。
- 需要与其他 Skill 对齐槽位和字段时，调用 `cstack-core` Skill；未安装时以本节为最小自足版。

## 目标

把跨会话的大工作画成一张共享地图，一次解决一个决策，直到通往目的地的路清楚。

## 地图

- **Destination**：到达终点是什么样（一份 spec、一个已锁的决策，或一次就地改动），一两行；每次会话先对齐。
- **Notes**：领域、该咨询的 Skill、持续偏好。
- **Decisions so far**：已关闭票据的索引，一行 gist 加链接，不重复细节。
- **Not yet specified（战争迷雾）**：知道要来、但现在还说不清的决策；能说清问题才升成票据。
- **Out of scope**：明确排除的工作，不再毕业。

## 决策票据类型

- **research**（AFK）：查资料，产出一个决策等待的事实。
- **prototype**（HITL）：做粗糙具体物，提升讨论保真度。
- **grilling**（HITL）：对话收敛决策，调用 `cstack-clarify`。
- **task**（HITL / AFK）：为解锁决策必须先做的手工工作。

## 前沿与阻塞

- 票据声明 blocked-by；无阻塞且未认领的构成前沿。
- 认领：先标记归属，再做，支持多会话并行。
- 迷雾只在目的地方向上聚集：能说清问题就开票，不能就留在 Not yet specified，不预切片。

## 两种调用

- **画图**：命名目的地（用 `cstack-clarify` / `cstack-domain-model`）→ 广度扫一遍找雾 → 建地图 → 建现在能说清的票据并连边 → 并行跑 research 票据 → 停。
- **推进**：读地图的低分辨率视图 → 选一张前沿票据并认领 → 解决（按 Notes 调用对应 Skill）→ 记录答案、关闭票据、更新 Decisions so far、把新能说清的雾毕业成票据。

## 停止与交接

规划本身不授权实现；目的地到达后交给 `cstack-specify` / `cstack-design` / `cstack-slice`。不建立与项目 issue / tracker 并行的持久状态。
