"""
色板接口

提供品牌色板数据的查询 API，供前端做本地颜色映射。
"""

from fastapi import APIRouter, HTTPException

from app.palette import PALETTES

router = APIRouter(prefix="/palette", tags=["色板"])


@router.get("")
async def get_all_palettes():
    """获取所有品牌的色板数据"""
    return {
        "brands": list(PALETTES.keys()),
        "palettes": PALETTES,
    }


@router.get("/{brand}")
async def get_brand_palette(brand: str):
    """获取指定品牌的色板数据"""
    brand_lower = brand.lower()
    if brand_lower not in PALETTES:
        raise HTTPException(
            status_code=404,
            detail=f"品牌 '{brand}' 不存在，可用品牌：{list(PALETTES.keys())}",
        )
    return {
        "brand": brand_lower,
        "count": len(PALETTES[brand_lower]),
        "colors": PALETTES[brand_lower],
    }
