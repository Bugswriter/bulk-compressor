from fastapi import FastAPI, HTTPException
import subprocess

app = FastAPI()

@app.get("/start")
async def start_service():
    try:
        subprocess.run(["sudo", "systemctl", "start", "dav-compressor.service"], check=True)
        return {"message": "Service started successfully"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail="Failed to start service")

@app.get("/stop")
async def stop_service():
    try:
        subprocess.run(["sudo", "systemctl", "stop", "dav-compressor.service"], check=True)
        return {"message": "Service stopped successfully"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail="Failed to stop service")
