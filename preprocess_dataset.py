import os
import cv2
import numpy as np
import random
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

# --------------------------- AUGMENTATIONS ---------------------------
def read_video(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return np.array(frames), fps

def write_video(frames, path, fps):
    if len(frames) == 0:
        return
    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, (w, h))
    for f in frames:
        out.write(f)
    out.release()

def crop_border_frames(frames, crop_amount=75):
    h, w = frames[0].shape[:2]
    return [f[:, crop_amount:w - crop_amount] for f in frames]

def mirror_frames(frames):
    return [cv2.flip(f, 1) for f in frames]

def change_brightness_frames(frames, factor=1.3):
    return [cv2.convertScaleAbs(f, alpha=factor, beta=0) for f in frames]

def grayscale_frames(frames):
    return [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]

def zoom_frames(frames, zoom_factor=1.1):
    h, w = frames[0].shape[:2]
    new_w, new_h = int(w / zoom_factor), int(h / zoom_factor)
    x1 = (w - new_w) // 2
    y1 = (h - new_h) // 2
    zoomed = [cv2.resize(f[y1:y1 + new_h, x1:x1 + new_w], (w, h)) for f in frames]
    return zoomed

def speed_frames(frames, factor=1.2):
    if factor > 1.0:
        step = int(factor)
        return frames[::step]
    else:
        repeat = int(1 / factor)
        out = []
        for f in frames:
            out.extend([f] * repeat)
        return out


# --------------------------- AUGMENTATION SELECTION ---------------------------
def apply_augmentation(frames, aug_name):
    if aug_name == "mirror":
        return mirror_frames(frames)
    elif aug_name == "bright":
        return change_brightness_frames(frames, factor=random.uniform(0.7, 1.3))
    elif aug_name == "gray":
        gray = grayscale_frames(frames)
        return [cv2.cvtColor(f, cv2.COLOR_GRAY2BGR) for f in gray] # convert 1-channel grayscale back to 3-channel for saving
    elif aug_name == "zoom":
        return zoom_frames(frames, zoom_factor=random.uniform(1.0, 1.25))
    elif aug_name == "fast":
        return speed_frames(frames, factor=random.uniform(1.2, 1.8))
    elif aug_name == "slow":
        return speed_frames(frames, factor=random.uniform(0.5, 0.9))
    elif aug_name == "crop":
        return crop_border_frames(frames, crop_amount=75)
    else:
        return frames

# pick 2 of these 4 options for augmentations
BUCKETS = {
    "mirror": ["mirror"],
    "color": ["bright", "gray"],
    "speed": ["fast", "slow"],
    "zoom": ["zoom"]
}


# --------------------------- WORKER FUNCTION ---------------------------
def process_video(args):
    input_path, output_dir, n_augs = args
    filename = os.path.splitext(os.path.basename(input_path))[0]

    # read and crop once
    frames, fps = read_video(input_path)
    frames = crop_border_frames(frames, crop_amount=75)

    for i in range(n_augs):
        # pick 2 random augmentation buckets
        chosen_buckets = random.sample(list(BUCKETS.keys()), 2)
        chosen_augs = [random.choice(BUCKETS[b]) for b in chosen_buckets]
        random.shuffle(chosen_augs)

        aug_tag = "_".join(chosen_augs)
        out_name = f"{filename}_AUG{i+1}_{aug_tag}.mp4"
        out_path = os.path.join(output_dir, out_name)

        f = frames
        for aug in chosen_augs:
            f = apply_augmentation(f, aug)

        write_video(f, out_path, fps)
    return filename


# --------------------------- MAIN ---------------------------
if __name__ == "__main__":
    #base_dir = "/Users/alimomennasab/Downloads/dataset/SL"
    base_dir = "/Users/alimomennasab/Downloads/WLASL_300/train"
    out_dir = "/Users/alimomennasab/Downloads/WLASL_300/train_augmented"
    n_augs_per_clip = 5  # number of augmented copies per original
    os.makedirs(out_dir, exist_ok=True)

    # collect all video paths
    all_videos = []
    for sign_label in sorted(os.listdir(base_dir)):
        sign_in_dir = os.path.join(base_dir, sign_label)
        if not os.path.isdir(sign_in_dir):
            continue

        sign_out_dir = os.path.join(out_dir, sign_label)
        os.makedirs(sign_out_dir, exist_ok=True)

        for f in os.listdir(sign_in_dir):
            if f.endswith(".mp4"):
                inp = os.path.join(sign_in_dir, f)
                all_videos.append((inp, sign_out_dir, n_augs_per_clip))

    print(f"Processing {len(all_videos)} total videos")

    max_workers = min(6, os.cpu_count() or 4)
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        list(tqdm(ex.map(process_video, all_videos), total=len(all_videos)))

