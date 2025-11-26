from typing import Protocol
from fastapi import FastAPI

class Handler(Protocol):
    def register(self, app: FastAPI, /) -> None: ...
