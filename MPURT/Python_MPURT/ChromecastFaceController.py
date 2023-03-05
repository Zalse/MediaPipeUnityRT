import pychromecast
import time
import cv2
import numpy as np
import FaceMeshModule
import math
from yeelight import Bulb

bulb = Bulb('192.168.0.34')
bulb.turn_on
chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["La télé"])
cast = chromecasts[0]
cast.wait()

print(cast)

cap = cv2.VideoCapture(0)
pTime = 0
actuTime = time.time()
detector = FaceMeshModule.FaceMeshDetector(refineLM=True)
#257/334
while True:
    success, img = cap.read()
    img, faces = detector.findFaceMesh(img, False)
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    if len(faces) != 0:
        eyebrowX, eyebrowY = faces[0][334][0], faces[0][334][1]
        eyebrowPos = eyebrowX, eyebrowY
        eyeLidX, eyeLidY = faces[0][386][0], faces[0][386][1]
        eyeLidPos = eyeLidX, eyeLidY
        cv2.circle(img,eyebrowPos,3,(255,255,255),cv2.FILLED)
        cv2.circle(img,eyeLidPos,3,(255,255,255),cv2.FILLED)
        cv2.line(img,eyeLidPos,eyebrowPos,(255,255,255), 1)

        centerX = (eyebrowX + eyeLidX) / 2
        centerY = (eyebrowY + eyeLidY) / 2
        center = int(centerX), int(centerY)
        cv2.circle(img, center, 2, (255, 255, 255), cv2.FILLED)

        length = math.hypot(eyeLidX - eyebrowY, eyeLidY - eyebrowY)
        vol = np.interp(length, [210, 230], [0, 1])
        intensity = np.interp(length, [210, 230], [0, 100])
        if (int(cTime - actuTime) > 1):
            #bulb.set_brightness(intensity)
            print(cast.set_volume(vol))
            actuTime += 0.5

    cv2.putText(img, str(int(fps)), (20, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, (0, 0, 0), 3)
    cv2.imshow("Image", img)
    cv2.waitKey(1)