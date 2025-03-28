from fastapi import FastAPI
from api.v1 import endpoints


app = FastAPI(
    swagger_ui_parameters = {"syntaxHighlight.theme": "obsidian"},
    title = "Smart API",
    version = "0.1.0"
)

app.include_router(router = endpoints.router, prefix = "/api/v1")
