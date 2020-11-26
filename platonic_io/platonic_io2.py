"""Main module."""
from time import time

import cv2

breakpoint()
cap = cv2.VideoCapture("grupaA1.mp4")
breakpoint()
frames = []

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

out = cv2.VideoWriter(
    "outpy.mp4",
    cv2.VideoWriter_fourcc("M", "P", "4", "V"),
    25,
    (frame_width, frame_height),
)
suma = 0.0
suma2 = 0.0
n = 0
while cap.isOpened():
    s2 = time()
    ret, frame = cap.read()
    suma2 += time() - s2
    if ret is True:
        # frames.append(frame)
        # cv2.imshow('Frame', frame)
        s = time()
        out.write(frame)
        suma += time() - s
        n += 1
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break
print(suma)
print(n / suma)
print(n / suma2)
cap.release()
out.release()

# breakpoint()
