import re
import os
import logging
import hashlib
from urllib.parse import urlparse
from ftplib import FTP
from dotenv import load_dotenv
import subprocess

def hash_encode(data):
    hash_object = hashlib.sha256(data.encode())
    return hash_object.hexdigest()

def get_ftp_credentials():
	load_dotenv()
	ftp_host = os.getenv("FTP_HOST")
	ftp_username = os.getenv("FTP_USER")
	ftp_password = os.getenv("FTP_PASS")
	return ftp_host, ftp_username, ftp_password

def get_ftp_connection():
    try:
        load_dotenv()
        ftp_host = os.getenv("FTP_HOST")
        ftp_user = os.getenv("FTP_USER")
        ftp_pass = os.getenv("FTP_PASS")

        if not ftp_host or not ftp_user or not ftp_pass:
            raise ValueError("FTP configuration missing in environment variables")

        ftp = FTP(ftp_host)
        ftp.login(ftp_user, ftp_pass)
        return ftp

    except Exception as e:
        print("An error occurred while establishing FTP connection:", e)
        return None

	

def davc_log(log_level, message):
    LOG_PATH = os.getenv("LOG_PATH")
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    if log_level == 1:
        logging.error(message)
    elif log_level == 0:
        logging.info(message)
    else:
        raise ValueError("Invalid log_level. Use 0 for INFO and 1 for ERROR")

def count_dav_files(ftp_connection, directory):
    try:
        file_count = 0
        ftp_connection.cwd(directory)
        dir_contents = ftp_connection.nlst()
        for item in dir_contents:
            if "." not in item:
                file_count += count_dav_files(ftp_connection, f"{directory}/{item}")
            elif item.endswith('.dav'):
                file_count += 1
        return file_count
    except Exception as e:
        return None

def get_file_size(file_path):
    try:
        parsed_url = urlparse(file_path)

        # Local file
        if parsed_url.scheme == '':
            size_bytes = os.path.getsize(file_path)
        
        # FTP file
        elif parsed_url.scheme == 'ftp':
            ftp = FTP(parsed_url.hostname)
            ftp.login(parsed_url.username, parsed_url.password)
            ftp.cwd(os.path.dirname(parsed_url.path))
            size_bytes = ftp.size(os.path.basename(parsed_url.path))
            ftp.quit()

        size_mb = size_bytes / (1024 * 1024)  # Convert bytes to MB
        return size_mb

    except Exception as e:
        print(f"Error getting file size: {e}")
        return None

def get_video_resolution(video_path):
    try:
        # Run ffprobe command to get video information
        result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', video_path], capture_output=True, text=True)
        
        # Parse the output to extract width and height
        resolution_str = result.stdout.strip()
        width, height = map(int, re.findall(r'\d+', resolution_str))
        
        return (width, height)
    except Exception as e:
        print(f"Error getting video resolution: {e}")
        return None
