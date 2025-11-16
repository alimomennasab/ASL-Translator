import os
import json
import shutil
import random

TOP_K = 100
JSON_PATH = "/Users/alimomennasab/Desktop/asldataset/WLASL/start_kit/WLASL_v0.3.json"
SOURCE_VID_DIR = "/Users/alimomennasab/Desktop/asldataset/WLASL/start_kit/videos"
OUTPUT_DIR = f"/Users/alimomennasab/Desktop/WLASL"
RAW_DIR = OUTPUT_DIR + f"/WLASL{TOP_K}"
TRAIN_DIR = OUTPUT_DIR + f"/WLASL{TOP_K}_train"
TEST_DIR = OUTPUT_DIR + f"/WLASL{TOP_K}_test"
VAL_DIR = OUTPUT_DIR + f"/WLASL{TOP_K}_val"

def load_metadata(json_path):
    with open(json_path, "r") as file:
        return json.load(file)

def count_videos_per_gloss(data):
    gloss_counts = {}

    for entry in data:
        gloss = entry["gloss"]
        gloss_counts[gloss] = gloss_counts.get(gloss, 0) + len(entry["instances"])

    return gloss_counts

def get_top_glosses(data, gloss_counts, target_k):
    sorted_items = sorted(gloss_counts, key=gloss_counts.get, reverse=True)
    valid_glosses = []

    for gloss in sorted_items:
        # Check if at least 3 videos (train/test/val) for this gloss exists
        video_count = 0
        for entry in data:
            if entry["gloss"] != gloss:
                continue

            for inst in entry["instances"]:
                video_path = os.path.join(SOURCE_VID_DIR, f"{inst['video_id']}.mp4")
                if os.path.exists(video_path):
                    video_count += 1
                if video_count >= 3:
                    valid_glosses.append(gloss)
                    break
                
            if gloss in valid_glosses:
                break

        if len(valid_glosses) >= target_k:
            break

    return valid_glosses


def copy_videos_for_gloss(data, glosses):
    if not os.path.exists(RAW_DIR):
        os.makedirs(RAW_DIR)

    filtered_entries = [entry for entry in data if entry["gloss"] in glosses]

    for entry in filtered_entries:
        gloss = entry["gloss"]
        gloss_folder = os.path.join(RAW_DIR, gloss)
        os.makedirs(gloss_folder, exist_ok=True)

        for instance in entry["instances"]:
            video_id = instance["video_id"]
            src = os.path.join(SOURCE_VID_DIR, f"{video_id}.mp4")
            dst = os.path.join(gloss_folder, f"{video_id}.mp4")

            if not os.path.exists(src):
                continue
            if os.path.exists(dst):
                continue

            shutil.copy2(src, dst)

def count_output(RAW_DIR):
    gloss_counts = {}

    for folder in os.listdir(RAW_DIR):
        if folder.startswith("."):
            continue

        folder_path = os.path.join(RAW_DIR, folder)

        if not os.path.isdir(folder_path):
            continue

        num_videos = len([f for f in os.listdir(folder_path) if f.endswith(".mp4")])
        gloss_counts[folder] = num_videos
        print(f"{folder}: {num_videos} videos")

    print(f"Total glosses: {len(gloss_counts)}")
    print(f"Total videos: {sum(gloss_counts.values())}")

import os, random, shutil

def train_test_split(RAW_DIR, TRAIN_DIR, TEST_DIR, VAL_DIR):
    random.seed(42)

    train_ratio, val_ratio, test_ratio = 0.8, 0.1, 0.1
    print(f"Train: {train_ratio}, Val: {val_ratio}, Test: {test_ratio}")

    for d in [TRAIN_DIR, VAL_DIR, TEST_DIR]:
        os.makedirs(d, exist_ok=True)

    glosses = [g for g in os.listdir(RAW_DIR) if os.path.isdir(os.path.join(RAW_DIR, g))]
    total_train, total_val, total_test = 0, 0, 0

    for gloss in sorted(glosses):
        src_dir = os.path.join(RAW_DIR, gloss)
        videos = [v for v in os.listdir(src_dir) if v.endswith(".mp4")]
        videos.sort()
        n = len(videos)
        if n == 0:
            continue

        random.shuffle(videos)

        # Compute counts (ensure at least 1 per split when n >= 3)
        if n >= 3:
            n_train = max(1, int(train_ratio * n))
            n_val = max(1, int(val_ratio * n))
            n_test = max(1, n - n_train - n_val)
        else:
            # for 1–2 videos, just split manually into 1 train, 0 val, rest test
            n_train = 1
            n_val = 0
            n_test = n - n_train - n_val

        # Slice
        train_videos = videos[:n_train]
        val_videos = videos[n_train:n_train + n_val]
        test_videos = videos[n_train + n_val:]

        # Copy files
        for split_videos, split_root in [
            (train_videos, TRAIN_DIR),
            (val_videos, VAL_DIR),
            (test_videos, TEST_DIR)
        ]:
            gloss_dst = os.path.join(split_root, gloss)
            os.makedirs(gloss_dst, exist_ok=True)

            for v in split_videos:
                shutil.copy2(os.path.join(src_dir, v), os.path.join(gloss_dst, v))

        total_train += len(train_videos)
        total_val += len(val_videos)
        total_test += len(test_videos)

        print(f"{gloss}: {len(train_videos):2d} train | {len(val_videos):2d} val | {len(test_videos):2d} test")

    print(f"Total videos: Train= {total_train}, Val= {total_val}, Test= {total_test}")


def main():
    data = load_metadata(JSON_PATH)
    gloss_counts = count_videos_per_gloss(data)

    print(f"Finding {TOP_K} glosses that actually have valid videos...")
    valid_glosses = get_top_glosses(data, gloss_counts, TOP_K)
    print(f"Found {len(valid_glosses)} valid glosses.")
    print("Top 10 valid glosses:", valid_glosses[:10])

    print("Copying videos")
    copy_videos_for_gloss(data, valid_glosses)
    print(f"WLASL{TOP_K} videos copied to: {RAW_DIR}")

    count_output(RAW_DIR)
    train_test_split(RAW_DIR, TRAIN_DIR, TEST_DIR, VAL_DIR)

if __name__ == "__main__":
    main()
