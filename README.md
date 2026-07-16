# Study Anything

让 AI 把任意领域搭建成一个可调研、可实践、可审查、可追溯、可持续接手的学习工作台。

Study Anything 不是课程清单生成器。它先调研领域，再结合学习者的背景和目标确定深度；每个教学模块由主 Agent 编写，再交给独立子 Agent 审查，修订通过后才进入学习。学习结果通过实践证据、验收和 Review 留痕。

## 核心特性

- 调研先行：用户不需要预先知道“应该学什么、学到多深”。
- 六条稳定命令：降低长期使用和跨 Agent 接手成本。
- 教学双角色：主 Agent 编写，独立子 Agent 审查。
- 审查门禁：未经审查的模块不能标记为“可学习”。
- 实践验收：不以课程数量、观看时长或笔记页数代表掌握。
- 双入口状态：总进度表负责全局追溯，模块 README 负责模块状态。
- 记录分离：模块 `审查/` 保存教学审查；根目录 `reviews/` 保存用户学习 Review。
- 平台中立：使用 Markdown、相对路径和可选 Python 标准库脚本。

## 六条常用命令

```text
Study Anything: Setup <学习内容和可选约束>
Study Anything: Master [学习项目路径]
Study Anything: Status
Study Anything: Continue
Study Anything: Record [可选的进展、认知或阻塞]
Study Anything: Assess [可选的模块 ID]
```

| 命令 | 用途 |
| --- | --- |
| `Setup` | 调研领域、确认学习深度并搭建学习工作台 |
| `Master` | 让新的 Agent 接手现有学习项目 |
| `Status` | 只读查看当前目标、模块、证据、阻塞和下一步 |
| `Continue` | 根据持久状态继续正确的下一项学习或内部流程 |
| `Record` | 保存学习进展、认知、失败或阻塞并更新进度 |
| `Assess` | 按模块验收标准检查证据并判断是否真正学会 |

同时兼容中文冒号，例如：

```text
Study Anything：Continue
```

## 工作方式

```text
领域调研
  → 用户背景与目标确认
  → 创建学习工作台
  → 主 Agent 编写模块
  → 独立子 Agent 审查
  → 主 Agent 修订与必要复审
  → 模块可学习
  → 用户实践与保存证据
  → 模块验收与学习 Review
  → 下一模块或综合项目
```

## 生成的工作台

```text
学习主题/
├─ README.md
├─ 使用文档.md
├─ 学习进度表.md
├─ 调研/
├─ 环境/
├─ modules/
│  └─ 01-主题/
│     ├─ README.md
│     ├─ notes/
│     ├─ practice/
│     ├─ tests/
│     ├─ evidence/
│     └─ 审查/
├─ reviews/
├─ capstone/
└─ .gitignore
```

`使用文档.md` 是新 Agent 快速理解架构并接手项目的入口；六条命令只定义在 Skill 中，不写入生成的学习项目。

## 安装

将整个 `study-anything` 目录放入支持 Agent Skills 的工具所使用的 skills 目录，并确保目录入口为 `SKILL.md`。不同工具的 skills 路径可能不同，请以对应工具文档为准。

Python 不是必需依赖。Python 3.9+ 只用于运行 `scripts/` 中的自动化脚本；没有 Python 时，Agent 可以按 Markdown 协议手工维护同样的结构和状态。

## 验证

```bash
python scripts/scaffold_workbench.py --root ./demo --title "示例主题"
python scripts/validate_workbench.py --root ./demo
```

模块进入“可学习”或“已学习”状态时，验证器会检查审查报告、学习证据、学习 Review 及总进度表的一致性。

## 许可证

[MIT](LICENSE)
