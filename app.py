import cv2
import mediapipe as mp
import datetime

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Gesture classification logic
def get_gesture(hand_landmarks):
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []
    landmarks = hand_landmarks.landmark

    # Thumb: compare x-coordinates
    if landmarks[tip_ids[0]].x < landmarks[tip_ids[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers: compare y-coordinates
    for id in range(1, 5):
        if landmarks[tip_ids[id]].y < landmarks[tip_ids[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    # Gesture logic
    if fingers == [1, 1, 1, 1, 1]:
        return "Open Palm"
    elif fingers == [0, 0, 0, 0, 0]:
        return "Fist"
    elif fingers == [0, 1, 1, 0, 0]:
        return "Peace Sign"
    elif fingers == [1, 0, 0, 0, 0]:
        return "Thumbs Up"
    else:
        return "Unknown"

# Start webcam
cap = cv2.VideoCapture(0)

# Get frame size and FPS from webcam
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
fps = int(cap.get(cv2.CAP_PROP_FPS)) or 20  # fallback to 20 if FPS not detected

# Unique filename with timestamp
filename = f"gesture_record_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"

# Define codec and create VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # or 'MJPG', 'mp4v'
out = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    gesture = "No Hand Detected"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = get_gesture(hand_landmarks)

    # Display gesture
    cv2.putText(frame, gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2, cv2.LINE_AA)

    # Write frame to video file
    out.write(frame)

    # Show output window
    cv2.imshow("Hand Gesture Recognition", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

# Release everything
cap.release()
out.release()
cv2.destroyAllWindows()
print(f"Recording saved as {filename}")
