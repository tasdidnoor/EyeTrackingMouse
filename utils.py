import numpy as np

def get_distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return np.linalg.norm(np.array(p1) - np.array(p2))

def get_ear(landmarks, eye_indices):
    """
    Calculate Eye Aspect Ratio (EAR) for a single eye.
    Vertical landmarks: indices 1, 5 and 2, 4
    Horizontal landmarks: indices 0, 3
    """
    # Vertical distances
    v1 = get_distance(landmarks[eye_indices[1]], landmarks[eye_indices[5]])
    v2 = get_distance(landmarks[eye_indices[2]], landmarks[eye_indices[4]])
    # Horizontal distance
    h = get_distance(landmarks[eye_indices[0]], landmarks[eye_indices[3]])
    
    return (v1 + v2) / (2.0 * h)

def is_dark(frame, threshold=20):
    """Detect if the frame is too dark (e.g., camera flap closed)."""
    gray = np.mean(frame)
    return gray < threshold
