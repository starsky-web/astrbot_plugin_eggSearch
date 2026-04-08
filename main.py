from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import pandas as pd
import os
from pathlib import Path
from typing import List


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


def load_egg_data(xlsx_path: str) -> List[EggData]:
    """从 XLSX 文件加载精灵蛋数据"""
    egg_list = []

    if not os.path.exists(xlsx_path):
        logger.warning(f"数据文件不存在: {xlsx_path}")
        return egg_list

    try:
        df = pd.read_excel(xlsx_path, engine='openpyxl')

        # 检查必要列是否存在
        required_columns = ['精灵名称', '尺寸最小', '尺寸最大', '重量最小', '重量最大']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.error(f"数据文件缺少必要列: {missing_cols}")
            return egg_list

        # 解析数据
        for _, row in df.iterrows():
            try:
                name = str(row['精灵名称'])
                size_min = float(row['尺寸最小'])
                size_max = float(row['尺寸最大'])
                weight_min = float(row['重量最小'])
                weight_max = float(row['重量最大'])

                # 跳过空行
                if pd.isna(name) or name.strip() == '':
                    continue

                egg_list.append(EggData(name, size_min, size_max, weight_min, weight_max))
            except (ValueError, TypeError) as e:
                logger.warning(f"数据值解析错误，跳过该行: {row.tolist()}, 错误: {e}")
                continue

    except Exception as e:
        logger.error(f"读取数据文件错误: {e}")

    logger.info(f"成功加载 {len(egg_list)} 条精灵数据")
    return egg_list


@register("eggSearch", "WJF", "洛克王国世界查蛋器", "0.1.0")
class EggSearchPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.egg_data: List[EggData] = []
        self.data_path: str = ""

    async def initialize(self):
        """插件初始化，加载数据"""
        # 获取插件目录下的 egg_data.xlsx
        self.data_path = str(Path(__file__).parent / "egg_data.xlsx")
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
