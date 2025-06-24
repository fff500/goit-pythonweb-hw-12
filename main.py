from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import utils, contacts, auth, users


app = FastAPI()


origins = ["<http://localhost:3000>", "http://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
