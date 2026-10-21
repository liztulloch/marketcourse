from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.Routes import stocks, chat

app = FastAPI(
    title="Market Course API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"message": "Market Course API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}