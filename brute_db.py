import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from yarl import URL

async def try_conn(host, password, db):
    db_url = URL.build(
        scheme="mysql+aiomysql",
        host=host,
        port=3306,
        user="root",
        password=password,
        path=f"/{db}"
    )
    engine = create_async_engine(str(db_url))
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
            return True, db_url
    except Exception as e:
        return False, str(e)
    finally:
        await engine.dispose()

async def main():
    hosts = ['127.0.0.1', 'localhost']
    pwds = ['root', '']
    dbs = ['cn_bookhub', 'cnm_bookhub_be']
    
    for h in hosts:
        for p in pwds:
            for d in dbs:
                print(f"Trying {h} / {p} / {d}...")
                ok, res = await try_conn(h, p, d)
                if ok:
                    print(f"SUCCESS! URL: {res}")
                    return
                else:
                    print(f"  Fail: {res[:100]}")

if __name__ == "__main__":
    asyncio.run(main())
