import pyautogui
import numpy as np
from screeninfo import get_monitors

pyautogui.FAILSAFE = False

class MouseController:
    def __init__(self, smoothing=0.9, sensitivity=2.5):
        monitor = get_monitors()[0]
        self.screen_w = monitor.width
        self.screen_h = monitor.height
        
        self.prev_x, self.prev_y = pyautogui.position()
        self.smoothing = smoothing
        self.sensitivity = sensitivity 
        
        self.buffer_size = 8
        self.x_buffer = []
        self.y_buffer = []

        self.deadzone = 0.005
        pyautogui.PAUSE = 0

    def move_to_relative(self, iris_offset, face_offset, eye_width):
        face_sensitivity = 1.0 

        norm_dx = (iris_offset[0] / eye_width) * self.sensitivity + (face_offset[0] / eye_width) * face_sensitivity
        norm_dy = (iris_offset[1] / eye_width) * self.sensitivity + (face_offset[1] / eye_width) * face_sensitivity
        
        if abs(norm_dx) < self.deadzone: norm_dx = 0
        if abs(norm_dy) < self.deadzone: norm_dy = 0

        target_x = (self.screen_w / 2) + (norm_dx * self.screen_w)
        target_y = (self.screen_h / 2) + (norm_dy * self.screen_h)
        
        self.x_buffer.append(target_x)
        self.y_buffer.append(target_y)
        if len(self.x_buffer) > self.buffer_size:
            self.x_buffer.pop(0)
            self.y_buffer.pop(0)
            
        avg_x = sum(self.x_buffer) / len(self.x_buffer)
        avg_y = sum(self.y_buffer) / len(self.y_buffer)

        curr_x = self.prev_x + (avg_x - self.prev_x) * (1 - self.smoothing)
        curr_y = self.prev_y + (avg_y - self.prev_y) * (1 - self.smoothing)
        
        curr_x = max(0, min(self.screen_w, curr_x))
        curr_y = max(0, min(self.screen_h, curr_y))
        
        pyautogui.moveTo(curr_x, curr_y)
        self.prev_x, self.prev_y = curr_x, curr_y

    def click(self):
        pyautogui.click()
