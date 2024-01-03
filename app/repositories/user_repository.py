from app.repositories.base_repository import Repository, AbstractRepository
from app.db.models import User


class UserRepository(Repository):
    model = User
