from fastapi import APIRouter

GreetingsRouter = APIRouter()


@GreetingsRouter.get("/")
def get_greeting():
    return {"greeting": "Hello, world!"}
