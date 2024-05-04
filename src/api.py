import uvicorn
from fastapi import FastAPI, HTTPException
import subprocess
from src.utils import get_ftp_connection, count_dav_files

app = FastAPI()

@app.get("/davc/start")
async def start_service():
    try:
        subprocess.run(["sudo", "systemctl", "start", "dav-compressor.service"], check=True)
        return {"message": "Service started successfully"}
    except subprocess.CalledProcessError as _:
        raise HTTPException(status_code=500, detail="Failed to start service")

@app.get("/davc/stop")
async def stop_service():
    try:
        subprocess.run(["sudo", "systemctl", "stop", "dav-compressor.service"], check=True)
        return {"message": "Service stopped successfully"}
    except subprocess.CalledProcessError as _:
        raise HTTPException(status_code=500, detail="Failed to stop service")

@app.get("/davc/stats")
async def total_videos():
    try:
        ftp_connection = get_ftp_connection()
        dav_input_count = count_dav_files(ftp_connection, '/AI/Input')
        dav_output_count = count_dav_files(ftp_connection, '/AI/Output')
        return {
			"total_uncompressed_videos": dav_input_count,			
			"total_compressed_videos": dav_output_count
		}
    except Exception as _:
        raise HTTPException(status_code=500, detail="Failed to get total videos count")
