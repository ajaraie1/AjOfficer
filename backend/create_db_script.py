import asyncio
import asyncpg
import os

# Hardcoded for reliability in this specific environment fix
# But reading from .env is better practice if possible.
# Let's try to read .env manually to avoid app dependency
def get_db_url():
    try:
        with open('.env') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    return line.strip().split('=', 1)[1]
    except Exception:
        pass
    return "postgresql://postgres:postgres@localhost:5432/igams"

async def create_database():
    url = get_db_url()
    print(f"Using database URL: {url}")
    
    # Parse database URL
    # format: postgresql://user:pass@host:port/dbname
    try:
        # standard postgres://user:pass@host:port/dbname
        parts = url.replace("postgresql://", "").split("/")
        user_pass_host_port = parts[0]
        dbname = parts[1]
    except Exception as e:
        print(f"Error parsing URL '{url}': {e}")
        return

    # Connect to default 'postgres' database
    sys_url = f"postgresql://{user_pass_host_port}/postgres"
    
    print(f"Connecting to system DB to check '{dbname}'...")
    try:
        conn = await asyncpg.connect(sys_url)
        
        # Check if DB exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", 
            dbname
        )
        
        if not exists:
            print(f"Database '{dbname}' does not exist. Creating...")
            await conn.execute(f'CREATE DATABASE "{dbname}"')
            print(f"Database '{dbname}' created successfully.")
        else:
            print(f"Database '{dbname}' already exists.")
            
        await conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    asyncio.run(create_database())
