"""
色板工具函数

提供颜色距离计算、最接近颜色匹配等通用工具。
"""

import math


def color_distance(rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> float:
    """
    加权欧几里得距离，权重模拟人眼对不同波长的感知敏感度

    R 权重 0.299  G 权重 0.587  B 权重 0.114
    """
    dr = rgb1[0] - rgb2[0]
    dg = rgb1[1] - rgb2[1]
    db = rgb1[2] - rgb2[2]
    return math.sqrt(0.299 * dr * dr + 0.587 * dg * dg + 0.114 * db * db)


def find_closest_color(target_rgb: tuple[int, int, int], palette: list[dict]) -> dict | None:
    """
    在指定色板中找到与目标 RGB 最接近的颜色

    Args:
        target_rgb: 目标颜色的 (R, G, B) 元组
        palette: 色板列表，每个元素需包含 'R'、'G'、'B' 字段

    Returns:
        色板中最接近的颜色项，色板为空时返回 None
    """
    if not palette:
        return None

    best = palette[0]
    best_dist = float('inf')
    for c in palette:
        dist = color_distance(target_rgb, (c['R'], c['G'], c['B']))
        if dist < best_dist:
            best_dist = dist
            best = c
    return best
