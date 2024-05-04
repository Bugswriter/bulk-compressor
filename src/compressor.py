import subprocess

def compress_video(input_filename, output_filename):
    command = [
        "ffmpeg",
        "-i", input_filename,
        "-vf", "fps=5,scale=640:360",
        "-c:v", "libx265",
        "-crf", "40",
        "-preset", "ultrafast",
        "-an",
        output_filename
    ]
    
    try:
        subprocess.run(command, check=True)
        print("Compression completed successfully!")
    except subprocess.CalledProcessError as e:
        print("Compression failed:", e)
