import uuid
import sqlite3
import os
import time
from video_compressor import compressor
from ftplib import FTP
from dotenv import load_dotenv

# input_filename = "sample.dav"
# output_filename = "output/output_sample.mp4"
# compressor.compress_video(input_filename, output_filename)


def get_ftp_credentials():
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve FTP host, username, and password from environment variables
    ftp_host = os.getenv("FTP_HOST")
    ftp_username = os.getenv("FTP_USER")
    ftp_password = os.getenv("FTP_PASS")

    return ftp_host, ftp_username, ftp_password

def fetch_dav_files(ftp, directory="/AI/Input", dav_files=[]):
    try:
        ftp.cwd(directory)
    except ftplib.error_perm as e:
        print(f"Failed to change directory: {e}")
        return

    files = ftp.nlst()

    for file in files:
        if file.endswith(".dav"):
            video_file_path = os.path.join(directory, file)
            ftp_host, ftp_user, ftp_pass = get_ftp_credentials()
            ftp_path_input = f"ftp://{ftp_user}:{ftp_pass}@{ftp_host}{video_file_path}"
            uuid_key = str(uuid.uuid4())
            temp_file_store_path = f"/tmp/{uuid_key}.mp4"
            print("Compressing ", video_file_path)
            compressor.compress_video(ftp_path_input, temp_file_store_path)
            print("Uploading ", temp_file_store_path)
            # ftp_upload(temp_file_store_path, video_file_path.replace('/AI/Input', '/AI/Output'))
            video_file_path = video_file_path
            ftp_upload(temp_file_store_path, '/AI/Output/')
            print("Adding record ", uuid_key)
            add_success_record(uuid_key, video_file_path)
            dav_files.append(video_file_path)
            quit()
        elif "." not in file:  # Directory
            fetch_dav_files(ftp, os.path.join(directory, file), dav_files)



def count_dav_files(ftp):
    dav_files = []
    fetch_dav_files(ftp, dav_files=dav_files)
    return len(dav_files)

def main():
    ftp_host, ftp_user, ftp_pass = get_ftp_credentials()
    ftp = FTP(ftp_host)
    print(ftp.login(ftp_user, ftp_pass))

    dav_files = []
    fetch_dav_files(ftp, dav_files=dav_files)

    print("List of all dav files (full path):")
    for file in dav_files:
        print(file)

    print("Total number of dav files:", len(dav_files))

    ftp.quit()

def create_remote_directories(ftp, full_path):
	print(ftp.cwd('/'))
	print(ftp.mkd('test'))


def ftp_upload(src_path, dst_path):
    print(src_path, dst_path)
    ftp_host, ftp_user, ftp_pass = get_ftp_credentials()
    ftp = FTP(ftp_host)
    print(ftp.login(ftp_user, ftp_pass))
    # create_remote_directories(ftp, dst_path)
	
    with open(src_path, 'rb') as file:
        ftp.storbinary('STOR ' + f"/AI/Output{dst_path}", file)

    ftp.quit()
    print("File uploaded successfully.")

def add_success_record(uuid_value, file_path):
    conn = sqlite3.connect('file_records.db')
    cursor = conn.cursor()

    record_data = (
        uuid_value,
        file_path,
        1,
        0
    )
    insert_query = """
    INSERT INTO files (id, full_file_path, is_compressed, is_aiocr)
    VALUES (?, ?, ?, ?)
    """
    cursor.execute(insert_query, record_data)
    conn.commit()
    cursor.close()
    conn.close()
    

if __name__ == "__main__":
    main()
