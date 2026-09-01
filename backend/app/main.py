import asyncio
import logging
import os
from contextlib import suppress
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db.init_db import seed_database
from app.routers import graph_explore_router, rag_router, router, workflow_router
from app.services.ai_provider import AIProviderError
from app.services.xunfei_virtual_human import cleanup_stale_sessions, stop_all_sessions
from app.services.source_trust import scheduled_source_validation


logger = logging.getLogger(__name__)


async def cleanup_virtual_human_sessions():
    while True:
        await asyncio.sleep(15)
        cleanup_stale_sessions()


async def refresh_source_trust_scores():
    interval = max(60, int(os.getenv("SOURCE_VALIDATION_INTERVAL_SECONDS", "3600")))
    initial_delay = max(0, int(os.getenv("SOURCE_VALIDATION_INITIAL_DELAY_SECONDS", "15")))
    await asyncio.sleep(initial_delay)
    while True:
        try:
            await asyncio.to_thread(scheduled_source_validation)
        except Exception:
            logger.exception("数据源交叉验证定时任务失败")
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    seed_database()
    cleanup_task = asyncio.create_task(cleanup_virtual_human_sessions())
    source_validation_task = asyncio.create_task(refresh_source_trust_scores())
    try:
        yield
    finally:
        cleanup_task.cancel()
        source_validation_task.cancel()
        with suppress(asyncio.CancelledError):
            await cleanup_task
        with suppress(asyncio.CancelledError):
            await source_validation_task
        stop_all_sessions()


app = FastAPI(title="数融智联岗位能力图谱构建与分析系统", version="1.0.0", lifespan=lifespan)


@app.exception_handler(AIProviderError)
async def ai_provider_error_handler(_request, exc: AIProviderError):
    return JSONResponse(status_code=502, content={"detail": str(exc)})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "shurong-zhilian", "status": "running"}


app.include_router(router)
app.include_router(graph_explore_router)
app.include_router(rag_router)
app.include_router(workflow_router)
