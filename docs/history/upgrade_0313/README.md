# Upgrade 0310 — Skill System Upgrade

本次升级的目标：优化 AutoService 元 Skill（brainstorming / planning-with-files / skill-creator），引入两层架构 + KB 切片 + subagent + 数据溯源，然后用升级后的元 Skill 重建 cinnox-demo。

## 文档清单

| 文件 | 内容 | 状态 |
|------|------|------|
| [skills-architecture.md](skills-architecture.md) | 当前全部 17 个 Skill 的分层分类、依赖关系、数据库结构、入口区分 | 完成 |
| [upgrade-plan.md](upgrade-plan.md) | 升级实施计划：Phase 1A (KB 基础设施) + Phase 1B (元 Skill) + Phase 2 (cinnox-demo) | 草案，待技术确认 |
| [questions-for-tech.md](questions-for-tech.md) | 需要技术人员确认的 7 个问题（从非技术人员需求整理而来） | 待确认 |

## 背景分析摘要

### 发现的问题

1. **web/server.py 与 _shared 脱钩** — d57eb42 commit 建立了完整的共享基础设施（Mock API、权限检查、多语言配置），但 web/server.py 在 UAT 迭代中重写了一套独立的 Mock 账户 + system prompt + 会话管理（106 行膨胀到 1297 行）。本次不修复，留到下一阶段。

2. **元 Skill 只支持单 Agent 工作流** — brainstorming / planning-with-files / skill-creator 缺少两层架构、KB 切片、subagent 协调、数据溯源等概念。

3. **KB 无领域切片** — 546 个 chunk 在一个平坦池子里，无 domain/region 标签，搜索无法按领域过滤。

4. **PDF 切块粗糙** — 600 字符页面缓冲切块，丢失标题/段落结构和页码信息。

### 决策记录

| 决策 | 选择 | 原因 |
|------|------|------|
| web/server.py | 本次不动 | 先专注 Skill 优化 |
| 优化范围 | Layer 1 元能力（brainstorming / planning-with-files / skill-creator） | 用户指定 |
| Subagent + 两层架构 | 当前就实现 | 用户要求 |
| Subagent 实现方式 | Python 脚本（kb_subagent.py），待技术确认 | 见 questions-for-tech.md #5 |

## 如何继续

1. 将 [questions-for-tech.md](questions-for-tech.md) 中的问题发给技术人员确认
2. 根据确认结果调整 [upgrade-plan.md](upgrade-plan.md)
3. 在 Claude Code 中说"读取 docs/upgrade_0310/upgrade-plan.md 继续"即可恢复工作
