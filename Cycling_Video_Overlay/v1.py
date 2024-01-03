import bisect
import subprocess
import shlex
import os
import cv2
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil import tz
import fitparse
from scipy import ndimage
import math

from overlays import BarOverlay, GaugeOverlay


def load_fit(fname):
    return fitparse.FitFile(fname)


def load_video(fname, rotated_video):
    cap = cv2.VideoCapture(fname)
    fps = cap.get(cv2.CAP_PROP_FPS)
    ht = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    wd = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    num_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    if rotated_video:
        return cap, int(num_frames), int(fps), int(wd), int(ht)
    else:
        return cap, int(num_frames), int(fps), int(ht), int(wd)


def get_video_start_time(fname, creation_time_at_start=True):
    # Get creation time
    commands = [
        f"ffprobe -v quiet -print_format flat -show_format {fname}",
        "grep creation_time",
        "cut -d= -f2-",
    ]

    for idx, command in enumerate(commands):
        if idx == 0:
            result = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        else:
            result = subprocess.Popen(
                shlex.split(command), stdin=result.stdout, stdout=subprocess.PIPE
            )

    result = result.communicate()
    result = (
        result[0].decode("utf-8").replace("\n", "").replace('"', "").replace("'", "")
    )
    result = result.split(".")
    creation_time = result[0]
    creation_time = datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S")

    # Get duration
    commands = [
        f"ffprobe -v quiet -print_format flat -show_format {fname}",
        "grep duration",
        "cut -d= -f2-",
    ]

    for idx, command in enumerate(commands):
        if idx == 0:
            result = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        else:
            result = subprocess.Popen(
                shlex.split(command), stdin=result.stdout, stdout=subprocess.PIPE
            )

    result = result.communicate()
    duration = (
        result[0].decode("utf-8").replace("\n", "").replace('"', "").replace("'", "")
    )

    start_time = creation_time
    if not creation_time_at_start:
        start_time -= timedelta(seconds=round(float(duration)))
    return start_time, float(duration)


def get_video_rotation(fname):
    command = f"ffprobe -v error -select_streams v:0 -show_entries stream_tags=rotate -of csv=p=0 {fname}"
    result = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    result = result.communicate()
    result = (
        result[0].decode("utf-8").replace("\n", "").replace('"', "").replace("'", "")
    )
    return int(result)


def convert_time(t):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    if isinstance(t, str):
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S")
    # Tell the datetime object that it's in UTC time zone since
    # datetime objects are 'naive' by default
    t = t.replace(tzinfo=from_zone)

    # Convert time zone
    return t.astimezone(to_zone)


def get_metric_time(f, name):
    metrics = {}
    for record in f.get_messages("record"):
        current_val = None
        for data in record:
            if data.name == name:
                current_val = data.value
            if data.name == "timestamp":
                current_time = data.value
        if current_val is None:
            continue
        current_time = convert_time(current_time)
        metrics[current_time] = current_val
    return metrics


def get_all_field_names(f):
    names = set()
    for record in f.get_messages("record"):
        for data in record:
            names.add(data.name)
    return names


def fill_missing_fit(fit_timestamps, metrics, metric_fill_values):
    num_timesteps = (fit_timestamps[-1] - fit_timestamps[0]).seconds + 1
    filled_metrics = [[i for _ in range(num_timesteps)] for i in metric_fill_values]
    filled_timestamps = [
        fit_timestamps[0] + timedelta(seconds=i) for i in range(num_timesteps)
    ]
    for idx, val in enumerate(fit_timestamps):
        put_idx = (val - fit_timestamps[0]).seconds
        for filled_metric, metric in zip(filled_metrics, metrics):
            filled_metric[put_idx] = metric[idx]
    return filled_timestamps, filled_metrics


def get_fit_start(fit_timestamps, video_start_time, video_start_delay):
    video_start_time = video_start_time + timedelta(seconds=video_start_delay)
    # Index into fit_timestamps
    start_idx = bisect.bisect(fit_timestamps, video_start_time)
    # Get delay between video start and signal
    time_skip = fit_timestamps[start_idx] - video_start_time
    return start_idx, time_skip.seconds


def interpolate_fps(fps, overlays_data):
    # overlays_data is at 1fps. Fill to match video fps
    num_overlays_data = len(overlays_data)
    interpolated_overlays = [[] for _ in range(num_overlays_data)]
    for i in range(len(overlays_data[0]) - 1):
        # Interpolate fps number of values
        for j in range(num_overlays_data):
            current_interpolated_vals = np.linspace(
                overlays_data[j][i], overlays_data[j][i + 1], fps + 1
            )
            interpolated_overlays[j] += current_interpolated_vals[:-1].tolist()

    return interpolated_overlays


def process(
    video,
    overlays,
    data,
    num_frames,
    video_start_delay,
    fps,
    ht,
    wd,
    video_rotation_angle,
):
    print(f"Writing {num_frames} frames")

    # Skip unwanted frames
    video.set(cv2.CAP_PROP_POS_FRAMES, video_start_delay * fps)

    out = cv2.VideoWriter(
        video_outname, cv2.VideoWriter_fourcc(*"MP4V"), fps, (out_wd, out_ht)
    )

    def rotate_image(image, angle):
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(
            image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR
        )
        return result

    if video_rotation_angle != 0:
        if video_rotation_angle == 90:
            cv2_rot_angle = cv2.cv2.ROTATE_90_CLOCKWISE
        elif video_rotation_angle == 270:
            cv2_rot_angle = cv2.ROTATE_90_COUNTERCLOCKWISE
        elif video_rotation_angle == 180:
            cv2_rot_angle = cv2.ROTATE_180

    for frame_idx in range(num_frames):
        _, cur_frame = video.read()
        if video_rotation_angle != 0:
            cur_frame = cv2.rotate(cur_frame, cv2_rot_angle)

        for overlay, val in zip(overlays, data):
            cur_frame = overlay.add_overlay(cur_frame, val[frame_idx])

        # Resize
        cur_frame = cv2.resize(cur_frame, (out_wd, out_ht))

        out.write(cur_frame)

    out.release()


def get_data_at_times(time_data, timestamps, fill):
    data = []
    for t in timestamps:
        if t in time_data:
            data.append(time_data[t])
        else:
            data.append(np.nan)

    if isinstance(fill, (int, float)):
        data = [fill if np.isnan(i) else i for i in data]
    elif fill == "nearest":
        mask = np.isnan(data)
        data[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), data[~mask])

    return data


##############################
# Input params
video_inname = "GX010007.MP4"
ext = str(Path(video_inname).suffix)
video_outname = video_inname.replace(ext, "_out" + ext)
video_path = f"{video_inname}"
out_wd, out_ht = 1920, 1080
video_start_delay = 0  # seconds
export_duration = 90  # seconds

fit_path = "2023-12-31-185816-ELEMNT BOLT 943C-473-0.fit"
print(f"\nProcessing: {video_inname}")
##############################


video_rotation_angle = get_video_rotation(video_path)
if video_rotation_angle == 90 or video_rotation_angle == 270:
    rotated_video = True
else:
    rotated_video = False
video, num_frames, fps, video_ht, video_wd = load_video(
    video_path, rotated_video=rotated_video
)
fit_data = load_fit(fit_path)

video_start_time, video_duration = get_video_start_time(video_path)
video_start_time = convert_time(video_start_time)
fit_times_powers = get_metric_time(fit_data, "power")
fit_times_kph = get_metric_time(fit_data, "speed")
# m/s to kph
fit_times_kph = {i: 3.6 * j for i, j in fit_times_kph.items()}
fit_times_cadences = get_metric_time(fit_data, "cadence")
# Add lag
data_lag = 20
fit_timestamps = [
    video_start_time + timedelta(seconds=i + video_start_delay - data_lag)
    for i in range(math.ceil(export_duration + 1))
]

fit_powers = get_data_at_times(fit_times_powers, fit_timestamps, fill=0)
fit_kphs = get_data_at_times(fit_times_kph, fit_timestamps, fill=0)
fit_cadences = get_data_at_times(fit_times_cadences, fit_timestamps, fill=0)
# print(fit_powers)
# print(fit_cadences)
# print(fit_kphs)


num_frames = export_duration * fps

# Linear interpolation for fps
num_samp = int(num_frames // fps)
overlays_data = [fit_powers, fit_kphs, fit_cadences]
overlay_interpolated_data = interpolate_fps(int(fps), overlays_data)


power_overlay = BarOverlay(
    ht=100,
    wd=600,
    x1=2850,
    y1=2100 - 200,
    name="WATTS",
    min_val=0,
    max_val=max(500, int(1.2 * max(fit_powers))),
    border_clr=(0, 0, 0),
    bar_clr=(245, 135, 66),
    border_wd_percent=0.008,
)
kph_overlay = GaugeOverlay(
    scale=1.0,
    x1=300,
    y1=2100 - 150,
    name="KPH",
    min_val=0,
    max_val=max(40, int(1.2 * max(fit_kphs))),
    gauge_clr=(108, 224, 180),
    dial_file_id="g1.png",
    gauge_file_id="meter.png",
    display_dtype="float",
)
cadence_overlay = GaugeOverlay(
    scale=1.0,
    x1=800,
    y1=2100 - 150,
    name="RPM",
    min_val=0,
    max_val=max(120, int(1.2 * max(fit_cadences))),
    gauge_clr=(108, 224, 180),
    dial_file_id="g2.png",
    gauge_file_id="meter.png",
    display_dtype="int",
)

overlays = [power_overlay, kph_overlay, cadence_overlay]

process(
    video,
    overlays,
    overlay_interpolated_data,
    num_frames,
    video_start_delay,
    fps,
    video_ht,
    video_wd,
    video_rotation_angle=video_rotation_angle,
)

print(f"\nSaved output to: {video_outname}")
