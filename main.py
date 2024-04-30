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
            # /AI/Input/TC_8343_DOON PUBLIC SCHOOL/DVR 5/XVR_ch1_main_20240413110001_20240413120001.dav
            ftp_host, ftp_user, ftp_pass = get_ftp_credentials()
            ftp_path_input = f"ftp://{ftp_user}:{ftp_pass}@{ftp_host}{video_file_path}"
            # ftp_path_output = f"ftp://{ftp_user}:{ftp_pass}@{ftp_host}{video_file_path.replace('/AI/Input','/Output')}"
            compressor.compress_video(ftp_path_input, '/tmp/test.mp4')
            time.sleep(2)
            quit()
            
            dav_files.append(video_file_path)
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

if __name__ == "__main__":
    main()
