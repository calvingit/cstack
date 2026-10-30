# core

CStack 的共享内核 Skill，**不自动触发**，由其他 Skill 通过 Skill tool 调用，或由用户显式调用。

- [`SKILL.md`](SKILL.md)：只做索引，说明何时读哪份文档。
- [`PRINCIPLES.md`](PRINCIPLES.md)：所有 Skill 共用的判断底线。
- [`ARTIFACTS.md`](ARTIFACTS.md)：6 个产物槽位的字段、所有权与 ID 约定。
- [`ROLES.md`](ROLES.md)：5 个核心角色与 3 个可选专业角色的责任契约、独立性与降级规则。

## 安装

整套安装时，把本目录与各 Skill 目录一起复制：

```bash
cp -R "$CSTACK_ROOT"/skills/* .agents/skills/
```

只安装单个 Skill 时可以不装本 Skill；每个 `SKILL.md` 的「底线 / 产物」小节已覆盖它自己的职责，可独立运行。装了 `core` 时，各 Skill 在需要对齐槽位与字段时调用它。

调用不扩大授权：本 Skill 只提供共享词汇，不替调用方做判断。
