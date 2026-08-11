import asyncio
import sys
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


origins = [
    'http://localhost:5173',  # Endereço padrão do Vite / React
    'http://127.0.0.1:5173',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
