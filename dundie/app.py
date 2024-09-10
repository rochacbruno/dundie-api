from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from asyncio import sleep
from .routes import main_router

app = FastAPI(
    title="dundie",
    version="0.1.0",
    description="dundie is a rewards API",
)

app.include_router(main_router)


app.add_middleware(
   CORSMiddleware,
   allow_origins=[
        "http://localhost:8001",
        "http://localhost",
        "https://server.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_mensagem(request: Request, make_response):  # callback
    # processa request
    response = await make_response(request)
    # processa response
    response.headers["x-mensagem"] = "Hello"
    # response.headers["Access-Control-Allow-Origin"] = "*"
    return response
