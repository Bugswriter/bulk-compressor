import os
import sqlite3
import time
import uuid
import hashlib
from ftplib import FTP

from dotenv import load_dotenv

from video_compressor import compressor


def hash_encode(data):
    hash_object = hashlib.sha256(data.encode())
    return hash_object.hexdigest()


def get_ftp_credentials():
    load_dotenv()
    ftp_host = os.getenv("FTP_HOST")
    ftp_username = os.getenv("FTP_USER")
    ftp_password = os.getenv("FTP_PASS")
    return ftp_host, ftp_username, ftp_password


def check_record_existence(uuid_key):
    load_dotenv()
    DB_PATH = os.getenv("DB_PATH")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    select_query = """
    SELECT id FROM files WHERE id = ?
    """
    cursor.execute(select_query, (uuid_key,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result is not None



def fetch_dav_files(ftp, directory="/AI/Input", dav_files=[]):
    try:
        ftp.cwd(directory)
    except ftplib.error_perm as e:
        print(f"Failed to change directory: {e}")
        return

    files = ftp.nlst()

    for file in files:
        if file.endswith(".dav"):
            process_dav_file(ftp, directory, file)
            dav_files.append(os.path.join(directory, file))
        elif "." not in file:  # Directory
            fetch_dav_files(ftp, os.path.join(directory, file), dav_files)


def process_dav_file(ftp, directory, file):
    video_file_path = os.path.join(directory, file)
    print(f"Processing {video_file_path.split('/')[-1]}...")

    ftp_host, ftp_user, ftp_pass = get_ftp_credentials()
    ftp_path_input = f"ftp://{ftp_user}:{ftp_pass}@{ftp_host}{video_file_path}"

    uuid_key = hash_encode(video_file_path)
    if check_record_existence(uuid_key):
        print("> Video Already Exist...")
        return

    temp_file_store_path = f"/tmp/{uuid_key}.mp4"

    print("Compressing ", video_file_path)
    compressor.compress_video(ftp_path_input, temp_file_store_path)

    print("Uploading ", temp_file_store_path)
    ftp_upload(ftp, temp_file_store_path, video_file_path.replace('/AI/Input', '/AI/Output'))

    print("Adding record ", uuid_key)
    add_success_record(uuid_key, video_file_path)


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


def ftp_upload(ftp, src_path, dst_path):
    try:
        create_directory_structure(ftp, dst_path)
    except Exception as e:
        print(f"{dst_path}")
        print(f"Error: {e}")

    with open(src_path, 'rb') as file:
        ftp.storbinary('STOR ' + os.path.basename(dst_path), file)

    ftp.cwd('/')
    print("File uploaded successfully.")


def create_directory_structure(ftp, file_path):
    ftp.cwd('/')
    path_parts = file_path.strip('/').split('/')
    path_parts.pop()
    for path in path_parts:
        if path not in ftp.nlst():
            ftp.mkd(path)
        ftp.cwd(path)


def add_success_record(uuid_value, file_path):
    load_dotenv()
    DB_PATH = os.getenv("DB_PATH")
    conn = sqlite3.connect(DB_PATH)
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
