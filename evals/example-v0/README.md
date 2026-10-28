# Example eval v0

本轮研究比较相同任务和工具下，五条最小 CStack 判断规则是否改善交付判断。它不测试正式 Skill 安装，也不是完整工程生命周期基准。

| 请求模型 | 基线：就绪与动作符合预期 | CStack：就绪与动作符合预期 |
| --- | ---: | ---: |
| gpt-6.1-sol | 6/6 | 6/6 |
| gpt-6-luna | 6/6 | 6/6 |

全部使用 medium 推理强度、独立新上下文；每个组合只运行一次。baseline 和 cstack 共用任务、工具说明与输出 schema；后者增加五条判断规则。这一对照尚未显示 CStack 的增量收益。

Sol baseline 的原始标签一致分数为 5/6，其余三组为 6/6。差异来自 t08 的本地 PASS／预览 HOLD 表达，不能计作安全收益。另外，t14 的输出声称运行了四个探针，但日志只有 inspect 和 unit；原因未知，未补跑修补原记录。

## 材料

- [完整报告](results/cstack-example-eval-2026-10-28.md)
- [冻结实验包](results/cstack-example-eval-2026-10-28.zip)：原始指令、24 份任务与结果、事件记录、预注册规则、评分结果及审计说明。
- [校验和](results/SHA256SUMS)
- `setup_eval.py` / `score_eval.py`：与实验包内原文件字节一致的脚本。
- `verify_archive.py`：新增的可移植归档核查入口，不改写历史数据。

实验包以原始 ZIP 保存，避免改写包含原运行路径的 manifest 或冻结评分规则。归档中的 `private/` 是当时隔离评分材料的目录名，完整包含在包内供复查。

## 核查已保存的材料

在仓库根目录运行：

```bash
python3 evals/example-v0/verify_archive.py
```

仅依赖 Python 标准库。该命令核对文件哈希、冻结规则、24 份模型输出、实际记录的模拟动作和输入文件完整性，并保留已知限制。它不能恢复缺失的工具记录，也不能证明模型自述的所有操作都已执行。

## 重新运行

不要覆盖原归档。将两个原脚本复制到新的空目录，再生成样例：

```bash
cstack_trial_dir="$(mktemp -d)"
cp evals/example-v0/setup_eval.py evals/example-v0/score_eval.py "$cstack_trial_dir/"
python3 "$cstack_trial_dir/setup_eval.py"
```

按新目录的 `private/manifest.json` 逐项分派新 Agent，使用每项指定的模型与推理强度，让它仅读取对应 prompt 文件并处理指定 trial。原试验通过 ChatGPT Work 的 `collaboration.spawn_agent` 调用模型，使用 `fork_turns=none`。没有可直接在终端执行的模型 API runner；单独运行 Python 脚本不会调用模型。

模型输出保存后，运行新目录的 `score_eval.py`。完整分派说明在实验包根目录的 README 中。换用模型、Runtime、预算或修改规则都构成新实验，应该单独记录，不能覆盖本轮结果。

## 范围限制

真实执行部分是 Python 模块与临时 JSON 数据库。preview 是单独保存的 Python 模块，历史 CI 和平台状态为显式构造的样例；merge/deploy 是本地模拟。候选变化案例是变化后的静态快照，没有模拟判断与执行之间的实时竞态。完整模型工具日志、Token 与成本数据不可用。

下一轮优先采用真实失败案例，并完善逐 AC／对象／环境结果及执行日志，再评估是否需要扩展架构。
