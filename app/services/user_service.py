from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from ..models.user import User, UserCreate
from typing import Optional
import time


def get_or_create_user(db: Session, zehn_id: str, first_name: str, last_name: str, phone_number: Optional[str] = None) -> User:
    max_retries = 3
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        try:
            user = db.query(User).filter(User.zehn_id == zehn_id).first()
            
            if user:
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                if phone_number:
                    user.phone_number = phone_number
                db.commit()
                db.refresh(user)
                return user
            
            user_data = UserCreate(
                zehn_id=zehn_id,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number
            )
            
            user = User(**user_data.dict())
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return user
            
        except OperationalError as e:
            if "SSL SYSCALL error" in str(e) or "EOF detected" in str(e):
                if attempt < max_retries - 1:
                    db.rollback()
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
            raise