import asyncio
import sys
from http import HTTPStatus

from fastapi import FastAPI

from app.routers import auth, items, sales, users

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title='Gerenciador de Vendas')

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(items.router)
app.include_router(sales.router)


@app.get('/', status_code=HTTPStatus.OK)
async def read_root():
    return {'message': 'ola mundo!'}
