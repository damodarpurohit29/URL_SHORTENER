from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from fastapi.responses import RedirectResponse

from url_shortener.db.session import get_db
from url_shortener.models.url_model import Url
from url_shortener.schemas.url_schema import ShortenResponse, ShortenRequest, StatsResponse
from url_shortener.utils import generate_short_code

router = APIRouter()

BASE_URL = "http://localhost:8000"

@router.post("/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
def shorten_url(payload: ShortenRequest, request: Request, db: Session = Depends(get_db)):

    if payload.custom_code:
        existing_code = db.query(Url).filter(Url.code == payload.custom_code).first()
        if existing_code:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Custom code already in use")
        code = payload.custom_code
    else:
        for _ in range(5):
            code = generate_short_code(6)
            if not db.query(Url).filter(Url.code == code).first():
                break
        else:
            raise HTTPException(status_code=500, detail="Failed to generate unique short code")


    existing_url = db.query(Url).filter(
        Url.target_url == str(payload.target_url),
        Url.expires_at == (datetime.utcnow() + timedelta(seconds=payload.expires_in_seconds) if payload.expires_in_seconds else None),
        Url.is_active == True
    ).first()
    if existing_url and not payload.custom_code:
        short_url = f"{BASE_URL}/{existing_url.code}"
        return ShortenResponse(
            code=existing_url.code,
            short_url=short_url,
            target_url=existing_url.target_url,
            created_at=existing_url.created_at,
            expires_at=existing_url.expires_at
        )

    expires_at = datetime.utcnow() + timedelta(seconds=payload.expires_in_seconds) if payload.expires_in_seconds else None

    new_url = Url(
        code=code,
        target_url=str(payload.target_url),
        expires_at=expires_at,
        is_active=True
    )
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    short_url = f"{BASE_URL}/{new_url.code}"
    return ShortenResponse(
        code=new_url.code,
        short_url=short_url,
        target_url=new_url.target_url,
        created_at=new_url.created_at,
        expires_at=new_url.expires_at
    )


@router.get("/{code}")
def redirect_to_url(code: str, db: Session = Depends(get_db)):
    url_entry = db.query(Url).filter(Url.code == code, Url.is_active == True).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")

    # Check expiration
    if url_entry.expires_at and url_entry.expires_at < datetime.utcnow():
        url_entry.is_active = False
        db.commit()
        raise HTTPException(status_code=410, detail="Short URL expired")

    # Update stats
    url_entry.visit_count += 1
    url_entry.last_accessed_at = datetime.utcnow()
    db.commit()

    return RedirectResponse(url=url_entry.target_url, status_code=307)


@router.get("/stats/{code}", response_model=StatsResponse)
def get_url_stats(code: str, db: Session = Depends(get_db)):
    url_entry = db.query(Url).filter(Url.code == code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")

    is_expired = False
    if url_entry.expires_at and url_entry.expires_at < datetime.utcnow():
        is_expired = True

    return StatsResponse(
        code=url_entry.code,
        target_url=url_entry.target_url,
        visit_count=url_entry.visit_count,
        created_at=url_entry.created_at,
        last_accessed_at=url_entry.last_accessed_at,
        expires_at=url_entry.expires_at,
        is_expired=is_expired
    )
