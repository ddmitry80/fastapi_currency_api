
from app.api.endpoints.auth.exceptions import InvalidCredentials
from app.api.endpoints.auth.security import check_password
from app.api.schemas.auth import UserCreate, UserFromDB


async def create_refresh_token(
        *, user_id: int, refresh_token: str | None = None
    ) -> str:
        if not refresh_token:
            refresh_token = utils.generate_random_alphanum(64)

        insert_query = insert(Token).values(
            uuid=uuid.uuid4(),
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(seconds=AuthConfig.REFRESH_TOKEN_EXP),
            user_id=user_id,
        )
        await execute(insert_query)

        return refresh_token


    # async def get_refresh_token(self, refresh_token: str) -> dict[str, Any] | None:
    #     select_query = select(Token).where(Token.refresh_token == refresh_token)
    #     return await fetch_one(select_query)


    async def expire_refresh_token(self, refresh_token_uuid: UUID4) -> None:
        update_query = (
            update(Token)
            .values(expires_at=datetime.utcnow() - timedelta(days=1))
            .where(Token.c.uuid == refresh_token_uuid)
        )

        await execute(update_query)


    async def authenticate_user(self, auth_data: UserCreate) -> UserFromDB:
        user = await self.get_user(email=auth_data.email)
        if not user:
            raise InvalidCredentials()

        if not check_password(auth_data.password, user["password"]):
            raise InvalidCredentials()

        return user