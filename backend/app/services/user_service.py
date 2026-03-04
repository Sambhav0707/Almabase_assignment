from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Fetch a user by email address. Returns None if not found."""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    """Fetch a user by primary key. Returns None if not found."""
    return await session.get(User, user_id)


async def create_user(session: AsyncSession, email: str, hashed_password: str) -> User:
    """Create a new user, commit, and return the refreshed instance."""
    user = User(email=email, hashed_password=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
