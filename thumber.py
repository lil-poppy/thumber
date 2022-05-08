import os
import subprocess
import time

def make_thumbnail(file):
    length = int(
        subprocess.check_output(
            f"ffprobe -i '{file}' -show_format -v quiet | sed -n 's/duration=//p' | awk '{{printf (\"%d\",$0)}}'",
            shell=True,
        ).decode("utf-8")
    )
    ty_res = time.gmtime(length / 2)
    res = time.strftime("%H:%M:%S", ty_res)
    os.system(
        f"ffmpeg -y -hide_banner -loglevel panic -ss {res} -i '{file}' -vframes 1 -q:v 1 {file}-thumb.jpg"
    )


def make_preview(file):
    org_file = file
    file = f"./{file}"
    length = int(
        subprocess.check_output(
            f"ffprobe -i '{org_file}' -show_format -v quiet | sed -n 's/duration=//p' | awk '{{printf (\"%d\",$0)}}'",
            shell=True,
        ).decode("utf-8")
    )
    count1 = 0
    file_list = []
    sec_list = ["00:00:02"]
    files = os.listdir()
    if f"{org_file}-preview.gif" in files:
        return
    if length < 3:
        pass
    elif length < 30:
        ty_res = time.gmtime(length / 2)
        res = time.strftime("%H:%M:%S", ty_res)
        sec_list.append(res)
        ty_res = time.gmtime(length - 2)
        res = time.strftime("%H:%M:%S", ty_res)
        sec_list.append(res)
    else:
        ty_res = time.gmtime(length / 2)
        res = time.strftime("%H:%M:%S", ty_res)
        sec_list.append(res)
        ty_res = time.gmtime(length - 30)
        res = time.strftime("%H:%M:%S", ty_res)
        sec_list.append(res)
    for sec in sec_list:
        for count2 in range(10, 60, 10):
            os.system(
                f"ffmpeg -y -hide_banner -loglevel panic -ss {sec}.{count2} -i '{org_file}' -vframes 1 -q:v 1 {file}-output{count1}.jpg"
            )
            os.system(
                f"convert {file}-output{count1}.jpg -resize 320x180 {file}-output{count1}.jpg"
            )
            file_list.append(f"{org_file}-output{count1}.jpg")
            count1 += 1
    os.system(
        f"convert -layers OptimizePlus -delay 10 -loop 0 -dispose previous {' '.join(img for img in file_list)} {file}-preview.gif"
    )
    os.system(f"rm {file}-output*")


def make_sprite(file, gpu=False):
    org_file = file
    file = f"./{file}"
    length = int(
        subprocess.check_output(
            f"ffprobe -i '{org_file}' -show_format -v quiet | sed -n 's/duration=//p' | awk '{{printf (\"%d\",$0)}}'",
            shell=True,
        ).decode("utf-8")
    )
    files = os.listdir()
    count1 = 0
    out_files = []
    time_left = length
    if length < 200:
        interval = 1
    else:
        interval = round(length / 200)
    sec = interval
    if f"{org_file}-sprite.jpg" in files:
        if gpu:
            os.system(
                f"ffmpeg -vsync 0 -hwaccel nvdec -c:v h264_cuvid -y -hide_banner -loglevel panic -ss 00:00:00 -i '{org_file}' -vframes 1 -q:v 1 {file}-output.jpg"
            )
        else:
            os.system(
                f"ffmpeg -y -hide_banner -loglevel panic -ss 00:00:00 -i '{org_file}' -vframes 1 -q:v 1 {file}-output.jpg"
            )
        os.system(f"convert {file}-output.jpg -resize 320x180 {file}-output.jpg")
        resolution = (
            subprocess.check_output(f"file {file}-output.jpg", shell=True)
            .decode("utf-8")
            .split("precision 8, ")[1]
            .split(",")[0]
            .split("x")
        )
        os.system(f"rm {file}-output*")
        return {
            "size": resolution,
            "path": f"{org_file}-sprite.jpg",
            "interval": interval,
            "duration": length,
        }
    if gpu:
        os.system(
            f"ffmpeg -vsync 0 -hwaccel nvdec -c:v h264_cuvid -y -hide_banner -loglevel panic -ss 00:00:00 -i '{org_file}' -vframes 1 -q:v 1 {file}-sprite.jpg"
        )
    else:
        os.system(
            f"ffmpeg -y -hide_banner -loglevel panic -ss 00:00:00 -i '{org_file}' -vframes 1 -q:v 1 {file}-sprite.jpg"
        )
    os.system(f"convert {file}-sprite.jpg -resize 320x180 {file}-sprite.jpg")
    while time_left > interval:
        res = time.strftime("%H:%M:%S", time.gmtime(sec))
        if gpu:
            os.system(
                f"ffmpeg -vsync 0 -hwaccel nvdec -c:v h264_cuvid -y -hide_banner -loglevel panic -ss {res} -i '{org_file}' -vframes 1 -q:v 1 {file}-output{count1}.jpg"
            )
        else:
            os.system(
                f"ffmpeg -y -hide_banner -loglevel panic -ss {res} -i '{org_file}' -vframes 1 -q:v 1 {file}-output{count1}.jpg"
            )
        os.system(
            f"convert {file}-output{count1}.jpg -resize 320x180 {file}-output{count1}.jpg"
        )
        os.system(
            f"convert {file}-sprite.jpg {file}-output{count1}.jpg -append '{file}-sprite.jpg'"
        )
        out_files.append(f"{file}-output{count1}.jpg")
        count1 += 1
        sec += interval
        time_left -= interval
    resolution = (
        subprocess.check_output(f"file {out_files[0]}", shell=True)
        .decode("utf-8")
        .split("precision 8, ")[1]
        .split(",")[0]
        .split("x")
    )
    os.system(f"rm {file}-output*")
    return {
        "size": resolution,
        "interval": round(interval),
        "duration": length,
    }


def thumber(file, gpu=False, preview=True, thumbnail=False):
    org_file = file
    try:
        if gpu:
            subprocess.check_output(
                f"ffmpeg -vsync 0 -hwaccel nvdec -c:v h264_cuvid -t 5 -loglevel panic -i '{org_file}' -f null -",
                shell=True,
            )
        else:
            subprocess.check_output(
                f"ffmpeg -t 5 -loglevel panic -i '{org_file}' -f null -", shell=True
            )
    except subprocess.CalledProcessError as rsp:
        if rsp.returncode != 0:
            return False
    result = make_sprite(org_file)
    if preview:
        make_preview(org_file)
    if thumbnail:
        make_thumbnail(org_file)
    time.sleep(1)
    return result


def check_length(file):
    length = int(
        subprocess.check_output(
            f"ffprobe -i '{file}' -show_format -v quiet | sed -n 's/duration=//p' | awk '{{printf (\"%d\",$0)}}'",
            shell=True,
        ).decode("utf-8")
    )
    return length
