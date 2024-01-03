import logging
from typing import Annotated, Any
from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.endpoints.auth.dependencies import valid_refresh_token, valid_refresh_token_user, valid_user_create
from app.api.endpoints.auth.jwt import create_access_token, parse_jwt_user_data
from app.api.endpoints.auth.service import authenticate_user, create_refresh_token, expire_refresh_token, get_refresh_token_settings

from app.api.schemas.auth import AccessTokenResponse, JWTData, UserCreate, UserResponse
# from app.api.endpoints.auth.service import
from app.services.user import UserService 

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)

@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(auth_data: UserCreate = Depends(valid_user_create)) -> dict[str, str]:
    user = await UserService.create_user(auth_data)
    return {"email": user.email}


@router.get("/users/me", response_model=UserResponse)
async def get_my_account(jwt_data: JWTData = Depends(parse_jwt_user_data)) -> dict[str, str]:
    user = await UserService.get_user(id=jwt_data.user_id)
    return {"email": user.email}


@router.post("/users/tokens/json", response_model=AccessTokenResponse)
async def auth_user(auth_data: UserCreate, response: Response) -> AccessTokenResponse:
    logger.debug(f"auth_user: {auth_data.email=}")
    user = await authenticate_user(auth_data)
    refresh_token_value = await create_refresh_token(user_id=user["user_id"])

    response.set_cookie(**get_refresh_token_settings(refresh_token_value))

    return AccessTokenResponse(
        access_token=create_access_token(user=user),
        refresh_token=refresh_token_value,
    )


@router.post("/users/tokens", response_model=AccessTokenResponse)
async def auth_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response) -> AccessTokenResponse:
    username, password = form_data.username, form_data.password
    logger.debug(f"auth_user: {username=}")
    auth_data = UserCreate(email=form_data.username, password=form_data.password)
    user = await authenticate_user(auth_data)
    refresh_token_value = await create_refresh_token(user_id=user["user_id"])

    response.set_cookie(**get_refresh_token_settings(refresh_token_value))

    return AccessTokenResponse(
        access_token=create_access_token(user=user),
        refresh_token=refresh_token_value,
    )


@router.put("/users/tokens", response_model=AccessTokenResponse)
async def refresh_tokens(
    worker: BackgroundTasks,
    response: Response,
    refresh_token: dict[str, Any] = Depends(valid_refresh_token),
    user: dict[str, Any] = Depends(valid_refresh_token_user),
) -> AccessTokenResponse:
    refresh_token_value = await create_refresh_token(
        user_id=refresh_token["user_id"]
    )
    response.set_cookie(**get_refresh_token_settings(refresh_token_value))

    worker.add_task(expire_refresh_token, refresh_token["uuid"])
    return AccessTokenResponse(
        access_token=create_access_token(user=user),
        refresh_token=refresh_token_value,
    )


@router.delete("/users/tokens")
async def logout_user(
    response: Response,
    refresh_token: dict[str, Any] = Depends(valid_refresh_token),
) -> None:
    await expire_refresh_token(refresh_token["uuid"])

    response.delete_cookie(
        **get_refresh_token_settings(refresh_token["refresh_token"], expired=True)
    )
