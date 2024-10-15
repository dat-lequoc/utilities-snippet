import subprocess
import sys

def get_video_duration(filename):
    """Get the duration of the video file in seconds."""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of',
        'default=noprint_wrappers=1:nokey=1', filename
    ]
    output = subprocess.check_output(cmd).decode('utf-8').strip()
    return float(output)

def split_video(input_file, num_parts=3):
    """Split the input video file into specified number of parts."""
    total_duration = get_video_duration(input_file)
    part_duration = total_duration / num_parts

    for i in range(num_parts):
        start_time = i * part_duration
        output_file = f'part_{i+1}.mkv'
        cmd = [
            'ffmpeg', '-i', input_file, '-ss', str(start_time),
            '-t', str(part_duration), '-c', 'copy', output_file
        ]
        print(f"Creating {output_file} from {start_time:.2f} to {start_time + part_duration:.2f} seconds")
        subprocess.run(cmd)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python split_video.py input_file.mp4")
        sys.exit(1)
    input_file = sys.argv[1]
    split_video(input_file)

