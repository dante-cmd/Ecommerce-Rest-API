from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.database import get_db
from app.models.models import Interaction as InteractionModel, User as UserModel
from app.schemas.schemas import Interaction, InteractionCreate
from app.core.auth import get_current_user, oauth2_scheme

router = APIRouter()

@router.post("/",
             response_model=Interaction, 
             status_code=status.HTTP_201_CREATED)
async def create_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db)):
    
    # Create interaction with user info if authenticated, otherwise just IP
    db_interaction = InteractionModel(
        ip_id=interaction.ip_id,
        product_id=interaction.product_id,
        interaction_type=interaction.interaction_type,
        # interaction_metadata=interaction.interaction_metadata,
        # ip_address=client_ip if not current_user else None  
        # Only store IP for anonymous users
    )
    
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

@router.get("/", response_model=List[Interaction])
def read_interactions(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):
    
    if not current_user : #or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access interactions")
        
    if not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Not authorized to access interactions")
    
    interactions = db.query(InteractionModel).order_by(InteractionModel.id).offset(skip).limit(limit).all()
    return interactions

@router.get("/{interaction_id}", response_model=Interaction)
def read_interaction(
    interaction_id: int, 
    #request:Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):
    if not current_user : #or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access interactions")
        
    if not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Not authorized to access interactions")
        
    db_interaction = db.query(InteractionModel).filter(InteractionModel.id == interaction_id).first()
    if db_interaction is None:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return db_interaction