"""
批量导入图纸数据脚本（自动扫描缩略图文件夹）

用法：
    手动模式  python scripts/import_patterns.py
    监听模式  python scripts/import_patterns.py --watch  （文件变化自动入库）
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.pattern import Pattern

DATA_DIR = Path(os.getenv("PATTERNS_DATA_DIR", r"D:\Desktop\pieceabean-data\patterns"))
THUMB_DIR = DATA_DIR / "thumbnail"


def scan_and_import(db):
    existing = {p.thumbnail_url for p in db.query(Pattern.thumbnail_url).all()}
    added = 0
    for fname in sorted(os.listdir(THUMB_DIR)):
        if not fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            continue
        img_path = f"/static/patterns/thumbnail/{fname}"
        if img_path in existing:
            continue
        name = Path(fname).stem
        db.add(Pattern(
            title=name,
            thumbnail_url=img_path,
            blueprint_url=f"/static/patterns/full/{fname}",
            category="其他",
            width=0, height=0, beads_count=0,
        ))
        added += 1
        print(f"[+] {fname}")
    if added:
        db.commit()
        print(f"导入 {added} 张\n")
    return added


def main():
    db = SessionLocal()
    try:
        if "--watch" in sys.argv:
            print(f"监听目录: {THUMB_DIR}\n")
            seen = set(os.listdir(THUMB_DIR))
            while True:
                time.sleep(3)
                current = set(os.listdir(THUMB_DIR))
                new_files = current - seen
                if new_files:
                    for f in new_files:
                        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                            print(f"检测到新文件: {f}")
                    scan_and_import(db)
                seen = current
        else:
            scan_and_import(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
