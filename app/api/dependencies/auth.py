from app.api.schemas.auth import UserFromDB
from app.auth.jwt import get_current_user


from fastapi import Depends


from typing import Annotated


GetAuthenticatedUser = Annotated[UserFromDB, Depends(get_current_user)]