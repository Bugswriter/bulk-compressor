import uvicorn
from fastapi import FastAPI, HTTPException
import subprocess
from src.utils import (get_ftp_connection,
					   count_dav_files,
					   get_total_size_stats,
					   get_success_records)

app = FastAPI()

SERVICE_NAME="davc"

@app.get("/davc/start")
async def start_service():
    try:
        subprocess.run(["sudo", "systemctl", "start", f"{SERVICE_NAME}.service"], check=True)
        return {"message": "Service started successfully"}
    except subprocess.CalledProcessError as _:
        raise HTTPException(status_code=500, detail="Failed to start service")

@app.get("/davc/stop")
async def stop_service():
    try:
        subprocess.run(["sudo", "systemctl", "stop", f"{SERVICE_NAME}.service"], check=True)
        return {"message": "Service stopped successfully"}
    except subprocess.CalledProcessError as _:
        raise HTTPException(status_code=500, detail="Failed to stop service")

@app.get("/davc/stats")
async def davc_stats():
    try:
        ftp_connection = get_ftp_connection()
        dav_input_count = count_dav_files(ftp_connection, '/AI/Input')
        dav_output_count = count_dav_files(ftp_connection, '/AI/Output')
        total_sizes = get_total_size_stats()

        return {
			"total_uncompressed_videos": dav_input_count,			
			"total_compressed_videos": dav_output_count,
			"total_original_filesize": total_sizes['total_original_size'],
			"total_compressed_filesize": total_sizes['total_compressed_size']
		}
    except Exception as _:
        raise HTTPException(status_code=500, detail="Failed to get total videos count")


@app.get("/davc/records")
async def davc_records(page: int = None):
    try:
        if page is not None and isinstance(page, int):
            records = get_success_records(page)
        else:
            records = get_success_records(1)
        
        if records:
            return records
        else:
            raise HTTPException(status_code=404, detail="No records found")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get list of records")
