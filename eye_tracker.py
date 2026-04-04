import cv2
import mediapipe as mp
import numpy as np

class EyeTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Landmark indices
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        self.LEFT_IRIS = [468, 469, 470, 471, 472]
        self.RIGHT_IRIS = [473, 474, 475, 476, 477]

    def get_eye_data(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return None
        
        landmarks = results.multi_face_landmarks[0].landmark
        h, w, _ = frame.shape
        
        coords = np.array([(lm.x * w, lm.y * h) for lm in landmarks])
        
        left_eye_coords = coords[self.LEFT_EYE]
        right_eye_coords = coords[self.RIGHT_EYE]
        left_iris_coords = coords[self.LEFT_IRIS]
        right_iris_coords = coords[self.RIGHT_IRIS]

        left_center = np.mean(left_eye_coords, axis=0)
        right_center = np.mean(right_eye_coords, axis=0)

        left_width = np.linalg.norm(coords[33] - coords[133])
        right_width = np.linalg.norm(coords[362] - coords[263])

        face_center = coords[1]

        return {
            'left_eye': left_eye_coords,
            'right_eye': right_eye_coords,
            'left_center': left_center,
            'right_center': right_center,
            'left_width': left_width,
            'right_width': right_width,
            'left_iris': left_iris_coords,
            'right_iris': right_iris_coords,
            'face_center': face_center,
            'face_presence': True
        }
