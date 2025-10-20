from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.database import get_db
from app.models.models import UserInteraction as UserInteractionModel, User as UserModel
from app.schemas.schemas import UserInteraction, UserInteractionCreate
from app.core.auth import get_current_user, oauth2_scheme

router = APIRouter()

def get_client_ip(request: Request):
    """Extract client IP address from request"""
    # Check for forwarded headers
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # Get the first IP in the list (client IP)
        return forwarded_for.split(',')[0].strip()
    
    # Check for other common headers
    forwarded = request.headers.get('X-Forwarded-Host')
    if forwarded:
        return forwarded
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Fallback to client host
    return request.client.host # type: ignore


@router.post("/", 
             response_model=UserInteraction, 
             status_code=status.HTTP_201_CREATED)
async def create_interaction(
    interaction: UserInteractionCreate, 
    request: Request,
    db: Session = Depends(get_db)):
    # Try to get current user (optional)
    current_user = None
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            current_user = get_current_user(db, token)
    except:
        pass  # User is not authenticated, which is fine
    
    # Get client IP
    client_ip = get_client_ip(request)
    
    # Create interaction with user info if authenticated, otherwise just IP
    db_interaction = UserInteractionModel(
        user_id=current_user.id if current_user else None,
        product_id=interaction.product_id,
        # timestamp=interaction.timestamp,
        interaction_type=interaction.interaction_type,
        interaction_metadata=interaction.interaction_metadata,
        ip_address=client_ip if not current_user else None  # Only store IP for anonymous users
    )
    
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

@router.get("/", response_model=List[UserInteraction])
def read_interactions(
    # request: Request,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):
    if not current_user : #or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access interactions")
        
    if not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Not authorized to access interactions")
    
    interactions = db.query(UserInteractionModel).order_by(UserInteractionModel.id).offset(skip).limit(limit).all()
    return interactions

@router.get("/{interaction_id}", response_model=UserInteraction)
def read_interaction(
    interaction_id: int, 
    #request:Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):
    if not current_user : #or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access interactions")
        
    if not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Not authorized to access interactions")
        
    db_interaction = db.query(UserInteractionModel).filter(UserInteractionModel.id == interaction_id).first()
    if db_interaction is None:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return db_interaction