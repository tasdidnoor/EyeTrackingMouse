import numpy as np

def get_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def get_ear(landmarks, eye_indices):
    v1 = get_distance(landmarks[eye_indices[1]], landmarks[eye_indices[5]])
    v2 = get_distance(landmarks[eye_indices[2]], landmarks[eye_indices[4]])
    h = get_distance(landmarks[eye_indices[0]], landmarks[eye_indices[3]])
    return (v1 + v2) / (2.0 * h)

def is_dark(frame, threshold=20):
    gray = np.mean(frame)
    return gray < threshold
