import os
import sqlite3
import time
import ftplib
from src.utils import (get_ftp_credentials,
					   get_ftp_connection,
					   get_video_resolution,
					   hash_encode, davc_log,
					   get_file_size,
					   fetch_first_frame)
from src.compressor import compress_video
from src.ai import openai_frame_process
from dotenv import load_dotenv


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
    video_name = video_file_path.split('/')[-1]
    ftp_host, ftp_user, ftp_pass = get_ftp_credentials()
    ftp_path_input = f"ftp://{ftp_user}:{ftp_pass}@{ftp_host}{video_file_path}"
    uuid_key = hash_encode(video_file_path)
    image_path_output = f"/tmp/{uuid_key}.jpg"
	
    if check_record_existence(uuid_key):
        print(f"> {video_name} already exist, skipping...")
        return

    davc_log(0, f"STARTING - {video_name}")
    start_time = time.time()
    temp_file_store_path = f"/tmp/{uuid_key}.mp4"

    print("Compressing ", video_file_path)
    compress_video(ftp_path_input, temp_file_store_path)

    print("Uploading ", temp_file_store_path)
    ftp_upload(ftp, temp_file_store_path, video_file_path.replace('/AI/Input', '/AI/Output'))

    print("Fetching First Frame ", temp_file_store_path)
    fetch_first_frame(temp_file_store_path, image_path_output)

    print("OpenAI Processing Frame ", image_path_output)
    ai_response = openai_frame_process(image_path_output)
    print(ai_response)

    print("Adding record ", uuid_key)
    original_size = get_file_size(ftp_path_input)
    compressed_size = get_file_size(temp_file_store_path)
    resolution = get_video_resolution(temp_file_store_path)

    video_record_data = {
		"uuid_key": uuid_key,
		"file_path": video_file_path,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "resolution": resolution,
		"datetime": ai_response.get('datetime'),
		"text_in_image": ai_response.get('text_in_image'),
		"is_camera_tilted": "YES" if ai_response.get('is_camera_tilted') else "NO",
		"is_camera_tampered": "YES" if ai_response.get('is_camera_tampered') else "NO",
		"are_there_people_in_the_image": "YES" if ai_response.get('are_there_people_in_the_image') else "NO"
    }

    os.remove(temp_file_store_path)
    os.remove(image_path_output)
    add_success_record(video_record_data)
	
    end_time = time.time()
    time_took = end_time - start_time
    davc_log(0, f"FINISHED [{time_took:.2f} sec] - {video_name}")


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

def add_success_record(video_record_data):
    load_dotenv()
    DB_PATH = os.getenv("DB_PATH")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    record_data = tuple(video_record_data.values())
    
    print("Record data:", record_data)  # Print record_data for debugging

    insert_query = """
	INSERT INTO files
	(id, file_path, original_size, compressed_size, resolution, datetime, text_in_image, is_camera_tilted, is_camera_tampered, are_there_people_in_the_image)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	"""
	
    cursor.execute(insert_query, record_data)
    conn.commit()
    cursor.close()
    conn.close()
	
def main():
    ftp = get_ftp_connection()
    dav_files = []
    fetch_dav_files(ftp, dav_files=dav_files)

    print("List of all dav files (full path):")
    for file in dav_files:
        print(file)

    print("Total number of dav files:", len(dav_files))

    ftp.quit()
	
if __name__ == "__main__":
    main()
