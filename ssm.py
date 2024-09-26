import cv2
import numpy as np
from dik import PressKey, ReleaseKey, DIK_Y
import threading
import time
from misc import get_relative_region, HighlightSection, force_foreground_window, shutdown_pc, close_process
import mss
import win32gui
import winsound
from beep import load_beeps

# Global variables for controlling the threads
detection_thread = None
stop_event = threading.Event()


def compare_with_reference(region, reference_image_path, scales=[0.5, 1.0, 1.5, 2.0]):
    # Convert the captured region to grayscale
    region_gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

    # Initialize SIFT detector
    sift = cv2.SIFT_create()

    # Find keypoints and descriptors in the region
    kp1, des1 = sift.detectAndCompute(region_gray, None)

    best_similarity = 0
    best_match_img = None

    for scale in scales:
        # Load and resize the reference image
        reference_image = cv2.imread(reference_image_path, cv2.IMREAD_GRAYSCALE)
        scaled_reference_image = cv2.resize(reference_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

        # Find keypoints and descriptors in the reference image
        kp2, des2 = sift.detectAndCompute(scaled_reference_image, None)

        # BFMatcher with default params
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        # Apply ratio test
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        # Calculate similarity
        similarity = len(good_matches) / max(len(kp1), len(kp2))

        # Keep track of the best match
        if similarity > best_similarity:
            best_similarity = similarity
            best_match_img = scaled_reference_image

    return best_similarity, best_match_img






def capture_region(hwnd, region):
    left, top, width, height = region
    with mss.mss() as sct:
        monitor = {"left": left, "top": top, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)  # Convert from BGRA to RGB
        screenshot_path = "debug_region_ss.png"
        cv2.imwrite(screenshot_path, img)
        return img


def start_screenshot_comparison(hwnd, textbox, update_status, var1, var2, var3, manual_region=None, stop_event=None, auto_shutdown=None):
    global screenshot_path, reference_image_path
    
    shutdown_timeout = 300
    relative_coords = (680, 555, 790, 590)
    window_resolution = (800, 600)
    reference_image_path = "roi.png"
    
    # Get beep frequency and wavelength from the passed variables
    frequency = var1.get()
    wavelength = var2.get()
    load_beeps(textbox, var1, var2, var3, update_status)
    region = get_relative_region(hwnd, relative_coords, window_resolution, manual_region)
    if region:
        update_status(textbox, f"Region selected for SS comparing: {region}")
        HighlightSection(region)

    def comparison_thread():
        last_y_time = time.time()
        count = 0
        while not stop_event.is_set():
            try:
                captured_image = capture_region(hwnd, region)
            except Exception as e:
                update_status(textbox, f"Error capturing image: {e}")
                continue 

            # Unpack the similarity and screenshot path
            similarity, _ = compare_with_reference(captured_image, reference_image_path)
            current_time = time.time()

            if similarity > 0.15:  # Threshold for determining a match
                last_y_time = current_time  # Reset the timer when a match is detected
                update_status(textbox, f"Match found! Similarity: {similarity:.2f}")
                previous_hwnd = win32gui.GetForegroundWindow()
                force_foreground_window(hwnd)
                press_y_key()
                winsound.Beep(frequency, wavelength)
                force_foreground_window(previous_hwnd)
                count += 1
                update_status(textbox, f"sold {count} times.")
            else:
                if current_time - last_y_time > shutdown_timeout:
                    if auto_shutdown and auto_shutdown.get():  # Check if the auto-shutdown is enabled
                        close_process(hwnd)
                        shutdown_pc()
                        break
                else:
                    update_status(textbox, f"No match. Similarity: {similarity:.2f}<0.15 : {current_time - last_y_time:.0f}s")

            time.sleep(2)

    detection_thread = threading.Thread(target=comparison_thread)
    detection_thread.start()
    return detection_thread







def press_y_key():
    PressKey(DIK_Y)
    time.sleep(0.1)  # Sleep to simulate key press duration
    ReleaseKey(DIK_Y)
