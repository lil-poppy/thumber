import os, subprocess

def thumber(file):
    # I convert the file to ./file to acount for when the filename starts with a "-" whitch i had problems with in linux.
    # Both org_file and file are needed because some commands don't accept the format ./file
    org_file = file
    file = f"./{file}"
    # Using suprocess and ffprobe to get the length of the video
    length = int(subprocess.check_output(f"ffprobe -i '{org_file}' -show_format -v quiet | sed -n 's/duration=//p' | xargs printf %.0f	# get video length (seconds)", shell=True).decode('utf-8'))
    # Frames = 200 or the length of the video, whichever is smaller
    if length < 200:
        frames = length
        interval = 1
    else:
        frames = 200
        interval = length/frames
    # If the file already exists, get the resolution of one frame and return the data
    files = os.listdir()
    if f"{org_file}-sprite.jpg" in files:
        os.system(f"ffmpeg -y -hide_banner -loglevel panic -ss 00:00:01 -i '{org_file}' -vframes 1 -q:v 31 {file}-output.jpg")
        os.system(f"convert {file}-output.jpg -resize 160x90 {file}-output.jpg")
        resolution = subprocess.check_output(f"file {file}-output.jpg", shell=True).decode('utf-8').split("precision 8, ")[1].split(",")[0].split("x")
        os.system(f"rm {file}-output*")
        return({"size":resolution, "path":f"{org_file}-sprite.jpg", "interval": interval, "duration": length})
    # Converting the video length which is in seconds, in something that ffmpeg can understand, which is hh:mm:ss
    min = sec = hour = i = 0
    out_files = []
    while frames > 1:
        if sec < 10:
            st_sec = f"0{sec}"
        elif sec >= 60:
            min += 1
            sec = sec - 60
            st_sec = "00"
        else:
            st_sec = str(sec)
        if min < 10:
            st_min = f"0{min}"
        elif min == 60:
            hour += 1
            min = 0
            st_min = "00"
        else:
            st_min = str(min)
        if hour < 10:
            st_hour = f"0{hour}"
        else:
            st_hour = str(hour)
        # Getting a frame using ffmpeg. For JPEG output use -q:v to control output quality. Full range is a linear scale of 1-31 where a lower value results in a higher quality
        os.system(f"ffmpeg -y -hide_banner -loglevel panic -ss {st_hour}:{st_min}:{st_sec} -i '{org_file}' -vframes 1 -q:v 31 {file}-output{i}.jpg")
        out_files.append(f"{file}-output{i}.jpg")
        i += 1
        sec += interval
        frames -= 1
    # Convert all the files to a desired size using ImageMagick (in this case 160x90). This will keep aspect ratio. If you want to resize it to an absolute resolution use for ex 160x90!
    for o_file in out_files:
        os.system(f"convert {o_file} -resize 160x90 {o_file}")
    # Get the dimensions of a frame. This is usefull if you keep aspect ratio
    resolution = subprocess.check_output(f"file {out_files[0]}", shell=True).decode('utf-8').split("precision 8, ")[1].split(",")[0].split("x")
    # Creating the sprite file by appending the first 2 files to a file-sprite.jpg file
    os.system(f"convert {out_files[0]} {out_files[1]} -append '{file}-sprite.jpg'")
    # Appending every other file by overwriting the sprite file
    for o_file in out_files[2:]:
        os.system(f"convert {file}-sprite.jpg {o_file} -append '{file}-sprite.jpg'")
    time.sleep(1)
    # Delete the frames after wating one second, to make sure the last convert is done
    os.system(f"rm {file}-output*")
    # Returning a dict containing:
    #   - size: the resolution of a frame
    #   - path:
    #   - interval: time in seconds (float) between 2 frames
    #   - duration: the length in seconds (float) of the video
    return({"size":resolution, "path":f"{org_file}-sprite.jpg", "interval": interval, "duration": length})
