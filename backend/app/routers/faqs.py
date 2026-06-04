"""常见问题接口 —— 公开获取 + 管理端 CRUD"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQUpdate, FAQResponse

router = APIRouter(prefix="/faqs", tags=["常见问题"])


@router.get("/", response_model=list[FAQResponse])
def list_faqs(db: Session = Depends(get_db)):
    """获取所有可见问题（按 sort_order 升序排列）"""
    return (
        db.query(FAQ)
        .filter(FAQ.is_visible == True)
        .order_by(FAQ.sort_order.asc(), FAQ.id.asc())
        .all()
    )


@router.post("/", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
def create_faq(body: FAQCreate, db: Session = Depends(get_db)):
    """新增问题"""
    faq = FAQ(
        question=body.question,
        answer=body.answer,
        sort_order=body.sort_order,
        is_visible=body.is_visible,
    )
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


@router.put("/{faq_id}", response_model=FAQResponse)
def update_faq(faq_id: int, body: FAQUpdate, db: Session = Depends(get_db)):
    """编辑问题"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="问题不存在")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(faq, key, value)

    db.commit()
    db.refresh(faq)
    return faq


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faq(faq_id: int, db: Session = Depends(get_db)):
    """删除问题"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="问题不存在")
    db.delete(faq)
    db.commit()
