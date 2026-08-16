import asyncio
import asyncpg
from dotenv import dotenv_values

async def main():
    try:
        env = dotenv_values('.env')
        user = env.get('DB_USER', 'postgres')
        password = env.get('DB_PASSWORD', '')
        host = env.get('DB_HOST', '127.0.0.1')
        port = int(env.get('DB_PORT', 5432))
        dbname = env.get('DB_NAME', 'asat')
        
        print(f"Connecting to postgres to ensure {dbname} exists...")
        conn = await asyncpg.connect(user=user, password=password, host=host, port=port, database='postgres')
        exists = await conn.fetchval('SELECT 1 FROM pg_database WHERE datname = $1', dbname)
        if not exists:
            await conn.execute(f'CREATE DATABASE {dbname}')
            print('Database created')
        else:
            print('Database already exists')
        await conn.close()
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(main())
