import json
import os
import random

import numpy as np
import winsound
import re
import threading

import pyautogui
import time
import pytesseract
from PIL import Image
import cv2
from pynput import mouse

# Coordinates for the mouse click
x, y = 1800, 1000  # Change this to your desired coordinates
press_times = []
release_times = []
press_durations = []
release_durations = []


def extract_timestamp_from_screenshot(image_path):
    screenshot = Image.open(image_path)
    # Assuming the timestamp is in the top-right corner of the screenshot
    width, height = screenshot.size
    timestamp_area = (width - 100, 0, width, 30)  # Adjust as needed
    timestamp_image = screenshot.crop(timestamp_area)

    # Perform OCR to extract the timestamp
    custom_config = r'--oem 3 --psm 6 outputbase digits'  # Adjust as needed
    timestamp_text = pytesseract.image_to_string(timestamp_image, config=custom_config)  # Using single-line OCR mode

    return timestamp_text.strip()


def extract_timestamp(text):
    pattern = r'\d+:\d{2}.\d{3}'  # Regex pattern to match format like 0:19.342
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    else:
        return None


def process_screenshots(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            image_path = os.path.join(directory, filename)
            timestamp = extract_timestamp_from_screenshot(image_path)
            print(f"Extracted Timestamp from {filename}: {timestamp}")


class CompactJSONEncoder(json.JSONEncoder):
    def iterencode(self, obj, _one_shot=False):
        if isinstance(obj, list) and all(isinstance(i, float) for i in obj):
            return json.JSONEncoder().iterencode(obj)
        return super().iterencode(obj, _one_shot)


def press_release(p, r):
    pyautogui.mouseDown()
    time.sleep(p)  # down
    press_durations.append(p)

    pyautogui.mouseUp()
    time.sleep(r)  # up
    release_durations.append(r)


def click_mouse(x, y):
    click_count = 10
    press = 0.8
    release = 0.2

    pyautogui.moveTo(x, y)
    # Here starts the random input that is working

    press = random.uniform(9.8, 10.25)  # Random double between 0.7 and 0.9
    release = random.uniform(0.4, 0.6)  # Random double between 0.1 and 0.3
    print(press)
    press_release(press, release)

    click_count = 3
    while click_count > 0:
        # pyautogui.moveTo(x, y)
        press = random.uniform(0.4, 0.7)  # Random double between 0.7 and 0.9
        release = random.uniform(0.2, 0.3)  # Random double between 0.1 and 0.3
        print(press)
        press_release(press, release)
        click_count = click_count - 1

    press = random.uniform(4, 4.1)  # Random double between 0.7 and 0.9
    release = random.uniform(0.3, 0.6)  # Random double between 0.1 and 0.3
    print(press)
    press_release(press, release)

    # Egyenes vege, utolso kanyar:

    click_count = 4
    while click_count > 0:
        press = random.uniform(0.4, 0.5)  # Random double between 0.7 and 0.9
        release = random.uniform(0.15, 0.2)  # Random double between 0.1 and 0.3
        print(press)
        press_release(press, release)
        click_count = click_count - 1

    press_release(5, 0)

    pyautogui.moveTo(1070, 990)
    pyautogui.mouseDown()
    pyautogui.mouseUp()

    winsound.Beep(440, 1000)
    print("Mouse clicking thread finished.")
    finish_time = input("Enter the finish time: ")

    pyautogui.moveTo(1670, 990)
    pyautogui.mouseDown()
    pyautogui.mouseUp()
    pyautogui.mouseDown()
    pyautogui.mouseUp()

    # Start new run:
    time.sleep(1)
    pyautogui.moveTo(1670, 890)
    pyautogui.mouseDown()
    pyautogui.mouseUp()

    new_run = {
        "press_durations": press_durations,
        "release_durations": release_durations,
        "finish_time": finish_time
    }

    try:
        with open('race_data.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    data.append(new_run)

    with open('race_data.json', 'w') as file:
        json.dump(data, file, indent=4, cls=CustomJSONEncoder)

    pyautogui.moveTo(1080, 20)


class CustomJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._indent = kwargs.get('indent', None)

    def encode(self, obj):
        if isinstance(obj, list):
            return '[' + ', '.join(self.encode(el) for el in obj) + ']'
        if isinstance(obj, dict):
            items = []
            for key, value in obj.items():
                if key in ['press_durations', 'release_durations']:
                    items.append(f'"{key}": {self.encode(value)}')
                else:
                    items.append(f'"{key}": {self.encode(value)}')
            return '{' + ', '.join(items) + '}'
        return json.JSONEncoder.encode(self, obj)


def press_screenshot_keys():
    screenshot_interval = 5
    last_screenshot_time = time.time()

    i = 15
    while i > 0:
        current_time = time.time()

        if current_time - last_screenshot_time >= screenshot_interval:
            # pyautogui.hotkey('ctrl', 'shift', 's')
            take_screenshot()
            last_screenshot_time = current_time
            i = i - 1

        # time.sleep(1)  # Check every second if it's time to take a screenshot


def take_screenshot():
    region = (1470, 290, 420, 750)  # Change this to your desired region (left, top, width, height)
    screenshot = pyautogui.screenshot(region=region)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    screenshot.save(f"screenshot_{timestamp}.png")


def on_click(x, y, button, pressed):
    current_time = time.time()
    if button == mouse.Button.right and pressed:
        # Stop listener if right mouse button is pressed
        print(press_durations)
        return False
    if button == mouse.Button.left:
        if pressed:
            if release_times:
                # Calculate release duration as the time between the last release and this press
                release_duration = current_time - release_times[-1]
                release_durations.append(release_duration)
            press_times.append(current_time)
        else:
            release_times.append(current_time)
            # Calculate press duration as the time between the press and this release
            press_duration = current_time - press_times[-1]
            press_durations.append(press_duration)


def manual_input():
    # MANUAL ----------------------------------------------------------------------
    with mouse.Listener(on_click=on_click) as listener:
        print("START")
        listener.join()

    print("Mouse clicking thread finished.")
    finish_time = input("Enter the finish time: ")

    new_run = {
        "press_durations": press_durations,
        "release_durations": release_durations,
        "finish_time": finish_time
    }

    try:
        with open('race_data.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    data.append(new_run)

    with open('race_data.json', 'w') as file:
        json.dump(data, file, indent=4)
    # ----------------------------------------------------------- MANUAL END


def pad_sequences(sequences, maxlen, padding_value=0.0):
    padded_sequences = []
    for seq in sequences:
        if len(seq) < maxlen:
            padded_seq = seq + [padding_value] * (maxlen - len(seq))
        else:
            padded_seq = seq[:maxlen]
        padded_sequences.append(padded_seq)
    return padded_sequences


def test_ai_suggestion():
    press_durations.extend([
        9.080621,
        0.54125917,
        0.6407298,
        0.7293235,
        1.3925065,
        0.73826694,
        0.8577992,
        0.5849981,
        0.2697109,
        2.2249498,
        0.7397201,
        0.71773076,
        0.39989048,
        0.7224507,
        0.14547178,
        0.47149032,
        0.024872938,
        0.18584855,
        0.046324927,
        0.0,
        0.0,
        0.0023398604
    ])
    release_durations.extend([
        0.3476153,
        0.19698995,
        0.20059237,
        0.3462609,
        0.40030223,
        0.277192,
        0.31043145,
        0.06601588,
        0.30169293,
        0.1433881,
        0.087636165,
        0.12458006,
        0.25779924,
        0.2616045,
        0.052628804,
        0.11609329,
        0.046975214,
        0.0,
        0.0,
        0.0,
        0.0109741,
        0.0])
    pyautogui.moveTo(x, y)

    if len(press_durations) != len(release_durations):
        raise ValueError("Press durations and release durations must have the same length.")

    for p, r in zip(press_durations, release_durations):
        pyautogui.mouseDown()
        print(p)
        time.sleep(p)  # Duration for mouse down
        pyautogui.mouseUp()
        time.sleep(r)  # Duration for mouse up

    pyautogui.moveTo(1070, 990)
    pyautogui.mouseDown()
    pyautogui.mouseUp()

    print("Mouse clicking thread finished.")
    winsound.Beep(440, 1000)
    finish_time = input("Enter the finish time: ")

    new_run = {
        "press_durations": press_durations,
        "release_durations": release_durations,
        "finish_time": finish_time
    }

    try:
        with open('race_data.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    data.append(new_run)

    with open('race_data.json', 'w') as file:
        json.dump(data, file, indent=4, cls=CustomJSONEncoder)

    pyautogui.moveTo(1670, 990)
    pyautogui.mouseDown()
    pyautogui.mouseUp()
    pyautogui.mouseDown()
    pyautogui.mouseUp()

    # Start new run:
    time.sleep(1)
    pyautogui.moveTo(1670, 890)
    pyautogui.mouseDown()
    pyautogui.mouseUp()


if __name__ == "__main__":
    # time.sleep(2)
    # mouse_thread = threading.Thread(target=click_mouse, args=(x, y))
    # click_mouse.daemon = True
    # mouse_thread.start()

    # # Create and start the screenshot taking thread
    # screenshot_thread = threading.Thread(target=press_screenshot_keys)
    # screenshot_thread.daemon = True  # Allows the program to exit even if this thread is still running
    # screenshot_thread.start()

    # mouse_thread.join()

    test_ai_suggestion()

    # manual_input()

    print("All tasks completed.")

    winsound.Beep(440, 1000)
