from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import auth, hatcheries, ponds, water_samples, feed_events, dashboard

app = FastAPI(title="TideNursery API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    messages = []
    for err in errors:
        loc = ".".join(str(x) for x in err.get("loc", []) if x != "body")
        msg = err.get("msg", "校验失败")
        messages.append(f"{loc}: {msg}" if loc else msg)
    detail = "; ".join(messages) if messages else "请求参数校验失败"
    return JSONResponse(status_code=400, content={"detail": detail})


app.include_router(auth.router)
app.include_router(hatcheries.router)
app.include_router(ponds.router)
app.include_router(water_samples.router)
app.include_router(feed_events.router)
app.include_router(dashboard.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "TideNursery"}
