from fastapi import FastAPI
from routes import user

app = FastAPI()
app.include_router(user.router)
