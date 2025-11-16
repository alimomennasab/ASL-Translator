import os
import json
import shutil

TOP_K = 100 
JSON_PATH = "/Users/alimomennasab/Desktop/asldataset/WLASL/start_kit/WLASL_v0.3.json"
SOURCE_VID_DIR = "/Users/alimomennasab/Desktop/asldataset/WLASL/start_kit/videos"
OUTPUT_DIR = f"/Users/alimomennasab/Desktop/WLASL{TOP_K}"

def load_metadata(json_path):
    with open(json_path, "r") as file:
        return json.load(file)

def count_videos_per_gloss(data):
    gloss_counts = {}
    for entry in data:
        gloss = entry["gloss"]
        gloss_counts[gloss] = gloss_counts.get(gloss, 0) + len(entry["instances"])
    return gloss_counts

def get_top_glosses(gloss_counts, k):
    sorted_items = sorted(gloss_counts.items(), key=lambda x: x[1], reverse=True)
    top_glosses = [item[0] for item in sorted_items[:k]]
    return top_glosses

def copy_videos_for_gloss(data, top_glosses):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    filtered_entries = [entry for entry in data if entry["gloss"] in top_glosses]

    for entry in filtered_entries:
        gloss = entry["gloss"]
        gloss_folder = os.path.join(OUTPUT_DIR, gloss)
        os.makedirs(gloss_folder, exist_ok=True)

        for instance in entry["instances"]:
            video_id = instance["video_id"]
            src = os.path.join(SOURCE_VID_DIR, f"{video_id}.mp4")
            dst = os.path.join(gloss_folder, f"{video_id}.mp4")

            # skip missing videos
            if not os.path.exists(src):
                continue

            # skip if already copied
            if os.path.exists(dst):
                continue

            shutil.copy2(src, dst)

def count_output(output_dir):
    gloss_counts = {}

    for folder in os.listdir(output_dir):
        folder_path = os.path.join(output_dir, folder)

        if folder == ".DS_Store":
            continue

        if os.path.isdir(folder_path):
            gloss_counts[folder] = len([f for f in os.listdir(folder_path) if f.endswith(".mp4")])
        print(f"{folder}: {gloss_counts[folder]} videos")
    print(f"Total glosses: {len(gloss_counts)}")
    print(f"Total videos: {sum(gloss_counts.values())}")

def main():
    data = load_metadata(JSON_PATH)

    gloss_counts = count_videos_per_gloss(data)

    print(f"Selecting top {TOP_K} glosses")
    top_glosses = get_top_glosses(gloss_counts, TOP_K)
    print("Top 10 glosses:", top_glosses[:10])

    print("Copying videos")
    copy_videos_for_gloss(data, top_glosses)
    print(f"WLASL{TOP_K} videos copied to: {OUTPUT_DIR}")

    count_output(OUTPUT_DIR)

if __name__ == "__main__":
    main()
