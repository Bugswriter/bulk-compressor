import re
import os
import logging
import hashlib
from urllib.parse import urlparse
from ftplib import FTP
from dotenv import load_dotenv
import sqlite3
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
        return int(size_mb)

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
        return f"{width}x{height}"
    except Exception as e:
        print(f"Error getting video resolution: {e}")
        return None

def get_success_records(page):
    try:
        load_dotenv()
        DB_PATH = os.getenv("DB_PATH")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Access columns by name
        cursor = conn.cursor()

        offset = (page - 1) * 25  # Calculate the offset for pagination
        
        # Query to fetch records with pagination
        query = """
        SELECT * FROM files LIMIT 25 OFFSET ?
        """
        cursor.execute(query, (offset,))
        
        records = []
        for row in cursor.fetchall():
            # Convert each row to a dictionary
            record_dict = dict(row)
            records.append(record_dict)

        return records

    except Exception as e:
        print(f"Error fetching records: {e}")
        return None
	
def get_total_size_stats():
    try:
        load_dotenv()
        DB_PATH = os.getenv("DB_PATH")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Query to calculate the sum of original_size and compressed_size
        query = """
        SELECT SUM(original_size) AS total_original_size, SUM(compressed_size) AS total_compressed_size FROM files
        """
        cursor.execute(query)
        
        # Fetch the results
        result = cursor.fetchone()

        # Convert the result to a dictionary
        stats = {
            "total_original_size": result[0] if result[0] is not None else 0,
            "total_compressed_size": result[1] if result[1] is not None else 0
        }

        return stats

    except Exception as e:
        print(f"Error fetching stats: {e}")
        return None	
