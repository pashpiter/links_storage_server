import uvicorn
from fastapi import FastAPI, Body
import tldextract
from typing import Annotated


app = FastAPI()


@app.post('/visited_links')
async def post_handler(links: Annotated[list, Body(embed=True)]):
    r = []
    for link in links:
        ext = tldextract.extract(link)
        r.append(f'{ext.domain}.{ext.suffix}')
    return r


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
