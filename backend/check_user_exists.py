import asyncio
from app.database import async_session_maker
from app.auth.models import UserModel
from sqlalchemy import select

async def check_user():
    async with async_session_maker() as session:
        result = await session.execute(select(UserModel).filter_by(email='uam7vl@gmail.com'))
        user = result.scalars().first()
        if user:
            print(f'User found: {user.email}')
        else:
            print('User not found')

if __name__ == "__main__":
    asyncio.run(check_user())
