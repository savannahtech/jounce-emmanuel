from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import get_db, init_db
from models import LLMPerformance
from helpers import queue_task, rank_llms
from  simulator import generate_simulation_data
from fastapi_cache.backends.redis import RedisBackend
import aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", 6379)
    redis = await aioredis.create_redis_pool(f"redis://{redis_host}:{redis_port}", encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app.get("/api/rank/{metric_name}")
@cache(expire=None) 
def get_ranked_llms(metric_name: str, db: Session = Depends(get_db)):
    llms = db.query(LLMPerformance).filter(LLMPerformance.metric_name == metric_name).all()
    if not llms:
        raise HTTPException(status_code=404, detail="Metric not found")
    return rank_llms(llms)


def simulate_data(db: Session = Depends(get_db)):
    data = generate_simulation_data()

    # bulk save to the database
    db.bulk_save_objects(data)
    
    db.commit()
    # Invalidating cache when data is saved to db
    FastAPICache.clear()
    return {"message": "Simulation data generated"}

@app.get("/api/simulate")
def get_simulated_data():
    task_data = {"task":"simulate_data", "param":"{}" }
    queue_task(task_data)
    return {"message": "Task has been queued "}

app.mount("/frontend", StaticFiles(directory="frontend/build", html=True), name="frontend")
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")