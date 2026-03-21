Import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math
import urllib.request
import os
import tkinter as tk
from tkinter import filedialog
import winsound

--- 1. Auto-Download Model ---

model_path = 'face_landmarker.task'
if not os.path.exists(model_path):
print("Downloading the Face Landmarker AI model...")
url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
urllib.request.urlretrieve(url, model_path)
print("Download complete!")

--- 2. Setup MediaPipe ---

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
base_options=base_options,
num_faces=1,
running_mode=vision.RunningMode.IMAGE
)
landmarker = vision.FaceLandmarker.create_from_options(options)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

def euclidean_distance(point1, point2):
return math.hypot(point1[0] - point2[0], point1[1] - point2[1])

def calculate_ear(face_landmarks, eye_indices, img_w, img_h):
coords = []
for i in eye_indices:
lm = face_landmarks[i]
coords.append((int(lm.x * img_w), int(lm.y * img_h)))

v1 = euclidean_distance(coords[1], coords[5])  
v2 = euclidean_distance(coords[2], coords[4])  
h = euclidean_distance(coords[0], coords[3])  
 
return (v1 + v2) / (2.0 * h)

--- 3. App Variables & Thresholds ---

EAR_THRESHOLD = 0.25
EAR_CONSEC_FRAMES = 8

blink_count = 0
closed_frames = 0
eye_closed = False
alarm_on = False

--- 4. Video Source Selection ---

root = tk.Tk()
root.withdraw()

print("Select video source:")
print("1. Live Webcam")
print("2. Upload Video File")
choice = input("Enter 1 or 2: ")

if choice == '2':
file_path = filedialog.askopenfilename(
title="Select Video File",
filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
)
if not file_path:
print("No file selected. Exiting.")
exit()
cap = cv2.VideoCapture(file_path)
else:
cap = cv2.VideoCapture(0)

print("\n--- INSTRUCTIONS ---")
print("Click on the video window and press 'Enter', 'Esc', or 'q' to stop.")
print("--------------------\n")

--- 5. Main Processing Loop ---

while cap.isOpened():
success, frame = cap.read()
if not success:
print("Video stream ended.")
break

img_h, img_w, _ = frame.shape  
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)  
result = landmarker.detect(mp_image)  
 
if result.face_landmarks:  
    for face_landmarks in result.face_landmarks:  
         
        left_ear = calculate_ear(face_landmarks, LEFT_EYE, img_w, img_h)  
        right_ear = calculate_ear(face_landmarks, RIGHT_EYE, img_w, img_h)  
        avg_ear = (left_ear + right_ear) / 2.0  
         
        # --- 1. COUNTING LOGIC ---  
        if avg_ear < EAR_THRESHOLD:  
            closed_frames += 1     
            if closed_frames > 15:  
                closed_frames=15    
            eye_closed = True  
        else:  
            # Eyes just opened. Was it a blink or a drowsy state?  
            if eye_closed:  
                if closed_frames < EAR_CONSEC_FRAMES:  
                    # It was a normal blink. Count it and reset instantly.  
                    blink_count += 1  
                    closed_frames = 0  
                eye_closed = False  
              
            # If recovering from drowsiness, gradually cool down the meter  
            if closed_frames >= EAR_CONSEC_FRAMES:  
                closed_frames -= 1  # Ticks down by 1 frame per loop  
            else:  
                closed_frames = 0   # Once safely awake, reset fully  
                # --- 2. ALARM & UI LOGIC ---  
        # This runs independently based on the current closed_frames count  
        if closed_frames >= EAR_CONSEC_FRAMES:

extra_frames = closed_frames - EAR_CONSEC_FRAMES
confidence = min(99.9, 75.0 + (extra_frames * 5.0))

# Display the Warning and the cooling-down confidence score  
            cv2.putText(frame, f"DROWSY! Conf: {confidence:.1f}%", (10, 300),  
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)  
              
            # Keep alarm ringing  
            if not alarm_on:  
                alarm_on = True  
                winsound.PlaySound('alarm.wav', winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)  
        else:  
            # Stop the alarm immediately once confidence drops below 75%  
            if alarm_on:  
                winsound.PlaySound(None, winsound.SND_PURGE)  
                alarm_on = False  
         
        # --- DRAWING STATS ---  
        cv2.putText(frame, f"EAR: {avg_ear:.2f}", (30, 50),  
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  
        cv2.putText(frame, f"Blinks: {blink_count}", (30, 100),  
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)  
         
        for i in LEFT_EYE + RIGHT_EYE:  
            lm = face_landmarks[i]  
            x, y = int(lm.x * img_w), int(lm.y * img_h)  
            cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)  

cv2.imshow("Blink & Drowsiness Detection", frame)  
 
# --- EXIT LOGIC ---  
key = cv2.waitKey(1) & 0xFF  
if key == ord('q') or key == 13 or key == 27:  
    break

if alarm_on:
winsound.PlaySound(None, winsound.SND_PURGE)

cap.release()
cv2.destroyAllWindows()

This is my code . Analyze it. Dont need to reply
