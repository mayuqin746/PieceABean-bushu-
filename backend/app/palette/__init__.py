"""
品牌色板模块

提供三大拼豆品牌（Artkal / Hama / Perler）的统一色板数据，
以及颜色距离匹配等工具函数。

使用方式：
    from app.palette import PALETTES, find_closest_color

    artkal = PALETTES["artkal"]
    closest = find_closest_color((128, 64, 32), artkal)
"""

from app.palette.data import PALETTES, ARTKAL_COLORS, HAMA_COLORS, PERLER_COLORS
from app.palette.utils import color_distance, find_closest_color

__all__ = [
    "PALETTES",
    "ARTKAL_COLORS",
    "HAMA_COLORS",
    "PERLER_COLORS",
    "color_distance",
    "find_closest_color",
]
