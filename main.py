from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

load_dotenv()

from database import init_db
from dependencies import limiter, verify_api_key
from routers import jobs, messages, sessions

app = FastAPI(title="Mini ChatGPT")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(sessions.router, dependencies=[Depends(verify_api_key)])
app.include_router(messages.router, dependencies=[Depends(verify_api_key)])
app.include_router(jobs.router, dependencies=[Depends(verify_api_key)])


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health():
    return {"status": "ok"}
