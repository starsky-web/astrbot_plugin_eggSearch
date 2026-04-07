# 洛克王国世界查蛋器插件实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 AstrBot 查蛋器插件，根据精灵蛋尺寸和重量匹配精灵种类

**Architecture:** 单文件插件架构，main.py 包含所有逻辑；CSV 数据文件存放精灵数据；插件初始化时加载数据到内存，支持热重载

**Tech Stack:** Python 3.x, AstrBot API, csv 模块（标准库，无需额外依赖）

---

## Chunk 1: 数据文件与目录结构

### Task 1: 创建数据目录和 CSV 模板文件

**Files:**
- Create: `D:\pythonProject\astrbot_plugin_eggSearch\data\egg_data.csv`

- [ ] **Step 1: 创建 data 目录**

```bash
mkdir -p "D:/pythonProject/astrbot_plugin_eggSearch/data"
```

- [ ] **Step 2: 创建 CSV 数据模板文件**

创建 `D:\pythonProject\astrbot_plugin_eggSearch\data\egg_data.csv`：

```csv
精灵名称,尺寸最小,尺寸最大,重量最小,重量最大
示例精灵A,10.000,15.000,20.000,30.000
示例精灵B,12.500,18.500,25.000,35.000
```

注意：文件使用 UTF-8 with BOM 编码，确保中文兼容。

- [ ] **Step 3: 验证文件创建成功**

```bash
ls -la "D:/pythonProject/astrbot_plugin_eggSearch/data/"
```

Expected: 显示 `egg_data.csv` 文件

- [ ] **Step 4: Commit**

```bash
git add data/egg_data.csv
git commit -m "feat: 添加精灵蛋数据模板文件

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 2: 插件核心逻辑实现

### Task 2: 实现数据加载模块

**Files:**
- Modify: `D:\pythonProject\astrbot_plugin_eggSearch\main.py`（完全重写）

- [ ] **Step 1: 编写数据加载函数**

重写 `D:\pythonProject\astrbot_plugin_eggSearch\main.py`：

```python
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import csv
import os
from pathlib import Path
from typing import List, Dict, Optional


# 精灵数据结构
class EggData:
    def __init__(self, name: str, size_min: float, size_max: float, weight_min: float, weight_max: float):
        self.name = name
        self.size_min = size_min
        self.size_max = size_max
        self.weight_min = weight_min
        self.weight_max = weight_max

    def matches(self, size: float, weight: float) -> bool:
        """检查输入的尺寸和重量是否在范围内"""
        return self.size_min <= size <= self.size_max and self.weight_min <= weight <= self.weight_max


def load_egg_data(csv_path: str) -> List[EggData]:
    """从 CSV 文件加载精灵蛋数据"""
    egg_list = []

    if not os.path.exists(csv_path):
        logger.warning(f"数据文件不存在: {csv_path}")
        return egg_list

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)  # 跳过表头

            for row in reader:
                if len(row) < 5:
                    logger.warning(f"数据行格式错误，跳过: {row}")
                    continue

                try:
                    name = row[0]
                    size_min = float(row[1])
                    size_max = float(row[2])
                    weight_min = float(row[3])
                    weight_max = float(row[4])
                    egg_list.append(EggData(name, size_min, size_max, weight_min, weight_max))
                except ValueError as e:
                    logger.warning(f"数据值解析错误，跳过该行: {row}, 错误: {e}")
                    continue

    except UnicodeDecodeError as e:
        logger.error(f"数据文件编码错误: {e}")

    logger.info(f"成功加载 {len(egg_list)} 条精灵数据")
    return egg_list


@register("eggSearch", "WJF", "洛克王国世界查蛋器", "1.1.1")
class EggSearchPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.egg_data: List[EggData] = []
        self.data_path: str = ""

    async def initialize(self):
        """插件初始化，加载数据"""
        # 获取插件目录下的 data/egg_data.csv
        self.data_path = str(Path(__file__).parent / "data" / "egg_data.csv")
        self.egg_data = load_egg_data(self.data_path)
        logger.info(f"查蛋器插件初始化完成，数据路径: {self.data_path}")

    async def terminate(self):
        """插件销毁"""
        logger.info("查蛋器插件已销毁")

    @filter.command("egg")
    async def search_egg(self, event: AstrMessageEvent):
        """查蛋指令：/egg 尺寸 重量"""
        message_str = event.message_str.strip()

        # 解析参数
        parts = message_str.split()
        if len(parts) < 3:
            yield event.plain_result("参数格式错误，请使用：/egg 尺寸 重量")
            return

        try:
            size = float(parts[1])
            weight = float(parts[2])
        except ValueError:
            yield event.plain_result("请输入有效的数字")
            return

        # 检查数据是否加载
        if not self.egg_data:
            yield event.plain_result("数据文件不存在或无数据，请联系管理员")
            return

        # 匹配精灵
        matched = [egg for egg in self.egg_data if egg.matches(size, weight)]

        # 格式化输出
        size_str = f"{size:.3f}"
        weight_str = f"{weight:.3f}"

        if matched:
            # 按名称排序
            matched.sort(key=lambda x: x.name)
            names = "、".join([egg.name for egg in matched])
            result = f"【查询结果】\n输入：尺寸 {size_str}，重量 {weight_str}\n匹配精灵：{names}"
        else:
            result = f"【查询结果】\n输入：尺寸 {size_str}，重量 {weight_str}\n未找到匹配的精灵，请检查输入的尺寸和重量。"

        yield event.plain_result(result)

    @filter.command("egg_reload")
    async def reload_data(self, event: AstrMessageEvent):
        """重新加载数据指令：/egg_reload"""
        self.egg_data = load_egg_data(self.data_path)
        yield event.plain_result(f"数据已重新加载，当前共 {len(self.egg_data)} 条精灵数据")
```

- [ ] **Step 2: 验证代码语法正确**

```bash
python -m py_compile "D:/pythonProject/astrbot_plugin_eggSearch/main.py"
```

Expected: 无错误输出

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: 实现查蛋器插件核心功能

- 添加 CSV 数据加载模块
- 实现 /egg 指令（尺寸重量匹配）
- 实现 /egg_reload 指令（热重载数据）
- 完善输入验证和错误处理

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 3: 更新插件元数据

### Task 3: 更新 metadata.yaml

**Files:**
- Modify: `D:\pythonProject\astrbot_plugin_eggSearch\metadata.yaml`

- [ ] **Step 1: 更新 metadata.yaml 描述信息**

修改 `D:\pythonProject\astrbot_plugin_eggSearch\metadata.yaml`：

```yaml
name: astrbot_plugin_eggSearch
display_name: 洛克王国世界查蛋器
desc: 输入尺寸和重量，返回匹配的精灵种类。指令：/egg 尺寸 重量，/egg_reload 重载数据
version: v1.1.1
author: WJF
repo: https://github.com/starsky-web/astrbot_plugin_eggSearch
```

- [ ] **Step 2: Commit**

```bash
git add metadata.yaml
git commit -m "docs: 更新插件描述，添加指令说明

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 4: 最终验证与清理

### Task 4: 项目验证

- [ ] **Step 1: 检查项目文件结构**

```bash
ls -la "D:/pythonProject/astrbot_plugin_eggSearch/"
ls -la "D:/pythonProject/astrbot_plugin_eggSearch/data/"
```

Expected:
- `main.py` 存在
- `data/egg_data.csv` 存在
- `metadata.yaml` 存在

- [ ] **Step 2: 检查 CSV 文件内容**

```bash
cat "D:/pythonProject/astrbot_plugin_eggSearch/data/egg_data.csv"
```

Expected: 显示表头和示例数据行

- [ ] **Step 3: 检查 Python 语法**

```bash
python -m py_compile "D:/pythonProject/astrbot_plugin_eggSearch/main.py"
```

Expected: 无错误输出

- [ ] **Step 4: 更新 CLAUDE.md（如有必要）**

如果需要更新项目说明，修改 `D:\pythonProject\astrbot_plugin_eggSearch\CLAUDE.md` 补充指令信息。

---

## 验证测试计划

插件需要在 AstrBot 环境中进行实际测试：

1. **部署测试**：将插件部署到 AstrBot，验证插件加载成功
2. **指令测试**：
   - `/egg 12.5 25` - 测试正常匹配
   - `/egg` - 测试参数缺失提示
   - `/egg abc 12` - 测试非数字输入提示
   - `/egg_reload` - 测试热重载功能
3. **边界测试**：
   - 输入值等于边界值时的匹配
   - CSV 文件不存在时的提示
   - CSV 格式错误时的处理

---

## 文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `main.py` | 重写 | 插件核心逻辑 |
| `data/egg_data.csv` | 创建 | 精灵蛋数据模板 |
| `metadata.yaml` | 修改 | 更新插件描述 |