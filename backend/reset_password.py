import asyncio
from app.database import async_session_maker
from app.auth.models import UserModel
from app.auth.jwt import get_password_hash
from sqlalchemy import select

async def reset_password():
    async with async_session_maker() as session:
        result = await session.execute(select(UserModel).filter_by(email='uam7vl@gmail.com'))
        user = result.scalars().first()
        if user:
            print(f'User found: {user.email}. Resetting password...')
            user.hashed_password = get_password_hash('123456')
            session.add(user)
            await session.commit()
            print('Password reset to: 123456')
        else:
            print('User not found')

if __name__ == "__main__":
    asyncio.run(reset_password())
