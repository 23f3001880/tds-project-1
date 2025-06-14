from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routes.chatRoutes import chat
from core.rag import get_or_build_index
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from utils.shared_limiter import limiter

app = FastAPI()

app.state.index = get_or_build_index()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get('/')
@limiter.limit("20/minute")
async def root(request: Request):
    return JSONResponse({'message': 'Welcome to The TDS RAG Project API!'})

app.include_router(chat)



