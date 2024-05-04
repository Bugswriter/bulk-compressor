import os
import logging
import hashlib
from ftplib import FTP
from dotenv import load_dotenv

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
