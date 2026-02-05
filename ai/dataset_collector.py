import os
import time
import cv2

def collect_images(label, save_dir="dataset", interval=5):
    os.makedirs(f"{save_dir}/{label}", exist_ok=True)
    cap = cv2.VideoCapture(0)

    count = 0
    while True:
        ret, frame = cap.read()
        if ret:
            filename = f"{save_dir}/{label}/{label}_{count}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved {filename}")
            count += 1
            time.sleep(interval)

    cap.release()
