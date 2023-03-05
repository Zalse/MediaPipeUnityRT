import math
import time

import cv2
import numpy as np
import PoseModule

class VideoTraitement:
    def __init__(self):
        self.saved_pose = np.zeros((33,2))
        self.current_pose = np.zeros((33,2))
        self.detector = PoseModule.PoseDetector()
        self.isAllGood = False

    def display_distances(self, img):
        wrongCounter = 0
        for i in range(self.saved_pose.shape[0]):
            x1 = int(self.saved_pose[i][0])
            y1 = int(self.saved_pose[i][1])
            if (x1 != 0 and y1 != 0):
                x2 = int(self.current_pose[i][0])
                y2 = int(self.current_pose[i][1])
                distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                if distance < 50:
                    cv2.line(img, (x1,y1), (x2,y2), (0,255,0))
                elif distance < 100:
                    cv2.line(img, (x1,y1), (x2,y2), (255,255,0))
                    wrongCounter += 1
                else:
                    cv2.line(img, (x1,y1), (x2,y2), (255,0,0))
                    wrongCounter += 1
        if (wrongCounter == 0):
            self.isAllGood = True
        else:
            self.isAllGood = False
            #print(wrongCounter)
            #print(self.current_pose)

    def treatment(self, frame, saved_pose = np.zeros((33,2)), current_pose = np.zeros((33,2))):
        self.saved_pose = saved_pose
        self.current_pose = current_pose
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # mat = 1 / 10 * np.ones((6, 6))
        # frame = cv2.filter2D(frame, -1, mat)

        frame, poseLM = self.detector.findPose(frame)
        self.display_distances(frame)

        return frame, poseLM


def main():
    cap = cv2.VideoCapture(0)
    pTime = 0
    detector = PoseModule.PoseDetector()
    treatment = VideoTraitement()
    while True:
        success, img = cap.read()
        img, pose = detector.findPose(img, draw=False)
        img, _ = treatment.treatment(img, current_pose=pose)
        #if len(faces) != 0:
            #print(len(faces))
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (20, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, (0, 0, 0), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()
