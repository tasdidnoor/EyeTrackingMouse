import cv2
import time
import tkinter as tk
from PIL import Image, ImageTk
from eye_tracker import EyeTracker
from mouse_controller import MouseController
from utils import get_ear, is_dark
import numpy as np

# --- CONFIGURATION ---
BLINK_THRESHOLD = 0.22
DOUBLE_BLINK_INTERVAL = 0.5  # Seconds
LONG_CLOSE_THRESHOLD = 5.0   # Seconds
DARKNESS_THRESHOLD = 25      # Average pixel value

class EyeMouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eye Tracking Mouse")
        self.root.geometry("450x600")
        self.root.configure(bg="#FBFBFD") # Apple-style off-white

        self.tracker = EyeTracker()
        self.mouse = MouseController()
        self.is_active = False

        # --- UI LAYOUT ---
        self.header = tk.Label(root, text="Eye Control", font=("SF Pro Display", 28, "bold"), bg="#FBFBFD", fg="#1D1D1F")
        self.header.pack(pady=(60, 10))

        self.subhead = tk.Label(root, text="A work-in-progress accessibility tool", font=("SF Pro Display", 14), bg="#FBFBFD", fg="#86868B")
        self.subhead.pack(pady=(0, 40))

        # Stylized Start Button (Clean, rounded look)
        self.btn_frame = tk.Frame(root, bg="#FBFBFD")
        self.btn_frame.pack(pady=20)

        self.start_btn = tk.Button(
            self.btn_frame, 
            text="Turn On", 
            command=self.start_tracking,
            font=("SF Pro Display", 16, "bold"),
            bg="#0071E3", # Apple Blue
            fg="white",
            padx=40,
            pady=15,
            relief="flat",
            activebackground="#005bb5",
            activeforeground="white",
            cursor="hand2",
            bd=0
        )
        self.start_btn.pack()

        # Instruction Cards
        self.info_frame = tk.Frame(root, bg="#FBFBFD")
        self.info_frame.pack(pady=40, padx=50)

        instructions = [
            "• Blink twice rapidly to Click",
            "• Keep eyes closed for 5s to Stop",
            "• Cover camera to Stop"
        ]

        for text in instructions:
            lbl = tk.Label(self.info_frame, text=text, font=("SF Pro Display", 12), bg="#FBFBFD", fg="#424245", justify="left")
            lbl.pack(anchor="w", pady=5)

        self.status_label = tk.Label(root, text="System Ready", font=("SF Pro Display", 10, "bold"), bg="#FBFBFD", fg="#86868B")
        self.status_label.pack(side="bottom", pady=(10, 30))

        # --- TEST AREA ---
        self.test_area = tk.Label(
            root, 
            text="Test Clicking Here", 
            font=("SF Pro Display", 12, "bold"),
            bg="#F4F4F7", 
            fg="#1D1D1F",
            width=30,
            height=4
        )
        self.test_area.pack(pady=10)

        # State variables
        self.last_blink_time = 0
        self.eyes_closed_start_time = None
        self.center_offset = (0, 0)
        self.face_center_offset = (0, 0)
        
    def flash_test_area(self):
        self.test_area.config(bg="#34C759", text="CLICK DETECTED!")
        self.root.after(500, lambda: self.test_area.config(bg="#F4F4F7", text="Test Clicking Here"))

    def start_tracking(self):
        if self.is_active: return
        self.is_active = True
        self.status_label.config(text="Calibration: LOOK AT CENTER OF SCREEN", fg="#0071E3")
        self.root.iconify() 
        self.run_loop()

    def run_loop(self):
        cap = cv2.VideoCapture(0)
        is_calibrated = False
        
        while self.is_active:
            ret, frame = cap.read()
            if not ret: break
            
            if is_dark(frame, DARKNESS_THRESHOLD):
                self.is_active = False
                break

            data = self.tracker.get_eye_data(frame)
            if data:
                # Calculate EAR for blinks
                left_ear = get_ear(data['left_eye'], [0, 1, 2, 3, 4, 5])
                right_ear = get_ear(data['right_eye'], [0, 1, 2, 3, 4, 5])
                avg_ear = (left_ear + right_ear) / 2.0
                
                # Relative Eye Movement
                left_iris_center = np.mean(data['left_iris'], axis=0)
                right_iris_center = np.mean(data['right_iris'], axis=0)
                
                # Iris offset from eye center
                curr_dx = (left_iris_center[0] - data['left_center'][0] + right_iris_center[0] - data['right_center'][0]) / 2.0
                curr_dy = (left_iris_center[1] - data['left_center'][1] + right_iris_center[1] - data['right_center'][1]) / 2.0
                
                # Face center offset (Head movement)
                curr_face_dx = data['face_center'][0]
                curr_face_dy = data['face_center'][1]

                # Initial Calibration (First valid frame)
                if not is_calibrated:
                    self.center_offset = (curr_dx, curr_dy)
                    self.face_center_offset = (curr_face_dx, curr_face_dy)
                    is_calibrated = True
                    self.status_label.config(text="Tracking Active", fg="#34C759")

                # Apply calibration offsets (Negate X for natural movement)
                final_dx = -(curr_dx - self.center_offset[0])
                final_dy = curr_dy - self.center_offset[1]
                
                final_face_dx = -(curr_face_dx - self.face_center_offset[0])
                final_face_dy = curr_face_dy - self.face_center_offset[1]

                avg_eye_width = (data['left_width'] + data['right_width']) / 2.0
                self.mouse.move_to_relative((final_dx, final_dy), (final_face_dx, final_face_dy), avg_eye_width)

                # Gestures
                if avg_ear < BLINK_THRESHOLD:
                    if self.eyes_closed_start_time is None:
                        self.eyes_closed_start_time = time.time()
                    if time.time() - self.eyes_closed_start_time > LONG_CLOSE_THRESHOLD:
                        self.is_active = False
                else:
                    if self.eyes_closed_start_time:
                        duration = time.time() - self.eyes_closed_start_time
                        if 0.05 < duration < 0.3:
                            current_time = time.time()
                            if current_time - self.last_blink_time < DOUBLE_BLINK_INTERVAL:
                                self.mouse.click()
                                self.flash_test_area()
                                self.last_blink_time = 0
                            else:
                                self.last_blink_time = current_time
                        self.eyes_closed_start_time = None

            # Optional: Show frame (for debugging, can be removed)
            # cv2.imshow("Eye Tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.is_active = False
                break

        cap.release()
        cv2.destroyAllWindows()
        self.status_label.config(text="Mouse is OFF", fg="black")
        self.root.deiconify() # Show window again

if __name__ == "__main__":
    root = tk.Tk()
    app = EyeMouseApp(root)
    root.mainloop()
