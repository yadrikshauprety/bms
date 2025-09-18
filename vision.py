import cv2

def check_anemia(frame):
    # Basic example: check lip brightness
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lips_region = gray[200:250, 100:300]  # placeholder coordinates
    avg_color = lips_region.mean()
    if avg_color > 150:
        return "Warning: Possible anemia/dehydration (pale lips)."
    return "Looks normal."
