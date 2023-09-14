import time
from typing import Annotated

import redis
import tldextract
import uvicorn
from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

app = FastAPI()

REDIS_DATA_URL = "redis://localhost:6379"


async def connection() -> redis.Redis:
    """Настройка подключения к Redis"""
    conn = redis.StrictRedis(host='localhost', port=6379, db=0)
    return conn


@app.post('/visited_links')
async def post_handler(
    links: Annotated[list[str], Body(embed=True)]
) -> JSONResponse:
    """Получение сайтов из POST-запроса и внесение их в Redis"""
    try:
        conn = await connection()
        n = conn.zcard('timings') + 1
        conn.zadd('timings', {n: int(time.time())})
        domains = []
        for link in links:
            ext = tldextract.extract(link)
            domains.append(f'{ext.domain}.{ext.suffix}')
        conn.lpush(n, *set(domains))
        return JSONResponse({"status": "ok"}, status_code=201)
    except Exception as e:
        return JSONResponse({"status": str(e)}, status_code=400)


@app.get('/visited_domains')
async def get_handler(since: str, to: str) -> JSONResponse:
    """Получение списка посещенных сайтов за определенное время"""
    try:
        conn = await connection()
        ids = conn.zrangebyscore('timings', since, to)
        domains = []
        [(domains.extend(conn.lrange(id, 0, -1))) for id in ids]
        content = {"domains": sorted(set(domains)), "status": "ok"}
        return JSONResponse(jsonable_encoder(content), status_code=200)
    except Exception as e:
        return JSONResponse({"status": str(e)}, status_code=400)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
