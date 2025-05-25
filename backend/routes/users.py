# backend/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.models.user import User as UserModel, UserTypeEnum # Use UserModel to avoid confusion
from backend.database.schemas.user import UserCreate, UserResponse, UserUpdate, MemberUpdate, ProfileUpdate # Schemas
from backend.database.crud import user as crud_user # CRUD operations
from backend.auth import get_current_active_user # For authenticated operations

router = APIRouter(prefix="/users", tags=["Users"])

# Get a specific user by their DB user_id
@router.get("/{db_user_id}", response_model=UserResponse) # db_user_id is the integer PK
def get_user_by_db_id_endpoint(db_user_id: int, db: Session = Depends(get_db)):
    user = crud_user.get_user_by_id(db, db_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# Endpoint to get user by firebase_uid (more common for frontend to have this after login)
@router.get("/fb/{firebase_uid}", response_model=UserResponse)
def get_user_by_firebase_uid_endpoint(firebase_uid: str, db: Session = Depends(get_db)):
    user = crud_user.get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# Create a new user (typically handled by Auth0 callback, but useful for admin)
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user_in: UserCreate, db: Session = Depends(get_db)):
    # TODO: Add admin role check for this endpoint if it's not for self-registration
    existing_user = crud_user.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if not user_in.firebase_uid: # Firebase UID is crucial
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Firebase UID is required")
    
    return crud_user.create_user(db, user_in.dict())


# Update current authenticated user's profile
@router.put("/me/profile", response_model=UserResponse)
async def update_my_profile_combined( # Renamed for clarity
    profile_data: ProfileUpdate, # Use the combined Pydantic model
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    user_data_fields = UserUpdate.__fields__.keys()
    member_data_fields = MemberUpdate.__fields__.keys()

    user_update_dict = {}
    member_update_dict = {}

    for key, value in profile_data.dict(exclude_unset=True).items():
        if key in user_data_fields:
            user_update_dict[key] = value
        elif key in member_data_fields:
            member_update_dict[key] = value
    
    updated_user = None
    if user_update_dict:
        updated_user = crud_user.update_user(db, current_user.user_id, user_update_dict)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for update")

    if current_user.user_type == UserTypeEnum.member and member_update_dict:
        if not current_user.member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member profile not found.")
        crud_user.update_member_details(db, current_user.firebase_uid, member_update_dict)
        if updated_user: # If user was updated, refresh it to load member changes
            db.refresh(updated_user)
        else: # If only member details changed, refetch user to return updated state
            updated_user = crud_user.get_user_by_id(db, current_user.user_id)


    if not updated_user: # Should have been set if anything was updated
        updated_user = current_user # Return current state if nothing changed

    return updated_user

# Get all trainers (for selection dropdowns, etc.)
@router.get("/trainers/list", response_model=list[dict])
def get_trainers_list_endpoint(db: Session = Depends(get_db)):
    # TODO: Add role check if needed (e.g., only members/managers can see this)
    return crud_user.get_all_active_trainers_for_select(db)


# TODO: Delete user endpoint - ensure proper authorization (e.g., admin only, or self-delete)
# @router.delete("/{db_user_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_user_endpoint(
#     db_user_id: int,
#     current_user: UserModel = Depends(get_current_active_user), # For authorization
#     db: Session = Depends(get_db)
# ):
#     # Example: Allow admin to delete any user, or user to delete themselves
#     if not (current_user.user_type == UserTypeEnum.manager or current_user.user_id == db_user_id):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")
    
#     user_to_delete = crud_user.get_user_by_id(db, db_user_id)
#     if not user_to_delete:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to delete not found")

#     if not crud_user.delete_user(db, db_user_id):
#         # This case should ideally not be reached if user_to_delete was found
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user")
#     return

# Note: The original PUT /users/{user_id} was a bit ambiguous with user_id being str.
# The new /users/me/profile is for the logged-in user to update their own profile.
# If an admin needs to update any user, a separate endpoint /users/admin/{db_user_id} would be clearer.
# The `full_details.py` frontend page logic needs to adapt to call `/users/me/profile`.








# ------------------------------------------------------------------------

# from fastapi import APIRouter, Depends, HTTPException, Request
# from sqlalchemy.orm import Session
# from backend.database import get_db
# from backend.database.models.user import User
# from backend.database.schemas.user import UserCreate, UserResponse, UserUpdate, MemberUpdate
# from backend.database.crud.user import create_user, get_user_by_id, update_user, delete_user, update_member


# router = APIRouter(prefix="/users", tags=["Users"])

# @router.get("/{user_id}", response_model=UserResponse)
# def get_user_endpoint(user_id: str, db: Session = Depends(get_db)):  # Changed user_id to str
#     user = get_user_by_id(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# @router.post("/", response_model=UserResponse)
# def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
#     try:
#         return create_user(db, user.dict())
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @router.put("/{user_id}", response_model=UserResponse)
# async def update_user_endpoint(user_id: str, request: Request, db: Session = Depends(get_db)):
#     print(f'DEBUG: update_user_endpoint: user_id={user_id}')
#     try:
#         data = await request.json()
#         print(f"🔥 RAW REQUEST BODY: {data}")
        
#         # Split data into user and member data
#         user_data = {
#             "first_name": data.get("first_name"),
#             "last_name": data.get("last_name"),
#             "phone": data.get("phone"),
#             "date_of_birth": data.get("date_of_birth"),
#             "gender": data.get("gender")
#         }
        
#         member_data = {
#             "weight": data.get("weight"),
#             "height": data.get("height"),
#             "fitness_goal": data.get("fitness_goal"),
#             "fitness_level": data.get("fitness_level"),
#             "health_conditions": data.get("health_conditions")
#         }
        
#         # Remove None values
#         user_data = {k: v for k, v in user_data.items() if v is not None}
#         member_data = {k: v for k, v in member_data.items() if v is not None}
        
#         validated_user = UserUpdate(**user_data)
#         # Update user
#         user = update_user(db, user_id, validated_user.dict(exclude_unset=True))
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         # If member data exists, update member details
#         if any(member_data.values()):
#             update_member(db, user_id, member_data)
        
#         return user
        
#     except Exception as e:
#         print(f"❌ Validation error: {e}")
#         raise HTTPException(status_code=422, detail=str(e))

# @router.delete("/{user_id}")
# def delete_user_endpoint(user_id: str, db: Session = Depends(get_db)):  # Changed user_id to str
#     if not delete_user(db, user_id):
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"detail": "User deleted successfully"}
