# roles/

这里放**角色定义**。一个 Agent 团队不是"一堆会写代码的模型"，而是
一组**有明确边界、明确产出、明确移交规则**的角色。

- `role_template.md` —— 复制它来定义你自己的角色。
- 建议每个角色一个文件：`roles/researcher.md`、`roles/writer.md` …

> 经验：Agent 团队最常见的事故不是"不会做"，而是"做了不该做的 / 越界改了别人的东西"。
> 角色定义里写清 `forbidden`（禁区）和 `escalate_to`（移交对象），比写 `mission` 更重要。
