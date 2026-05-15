import asyncio
import time
import psutil
from fastapi import FastAPI
import uvicorn
from config.config import Config
from utils.logger import get_logger

logger = get_logger("EtherWeb")

app = FastAPI(
    title="Ether Userbot Dashboard", 
    description="System monitoring and heartbeat service for Ether Userbot"
)

def get_uptime():
    uptime_seconds = int(time.time() - Config.START_TIME)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    if minutes > 0: parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    
    return " ".join(parts)

@app.get("/")
async def root():
    return {
        "status": "online",
        "bot": "Ether Userbot",
        "version": "2.0.1",
        "uptime": get_uptime(),
        "stats": {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent
        }
    }

async def run_web_service():
    if not Config.WEB_SERVICE:
        logger.info("Web service is disabled via config.")
        return
        
    logger.info(f"System: WEB SERVICE ACTIVE (Port: {Config.PORT})")
    
    config = uvicorn.Config(
        app=app, 
        host="0.0.0.0", 
        port=Config.PORT, 
        log_level="error"
    )
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except asyncio.CancelledError:
        logger.warning("Web service cancelled and shutting down.")
    except Exception as e:
        logger.error(f"Web service error: {e}")
