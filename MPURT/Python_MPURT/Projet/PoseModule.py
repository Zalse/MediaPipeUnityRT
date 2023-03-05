import cv2
import mediapipe as mp
import time
import numpy as np

class PoseDetector:

    def __init__(self, min_detection_confidence = 0.5, min_tracking_confidence=0.5):
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5)

    def findPose(self, img, draw = True):
        self.imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(self.imgRGB)
        pose = np.zeros((33,3))

        if self.results.pose_landmarks :
            
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS, landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style())

            poseLM = []

            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                ih, iw, ic = img.shape
                if (lm.visibility > 0.5):
                    x, y, z = int(lm.x * iw), int(lm.y * ih), int(lm.z)
                    #print(z)
                else:
                    x, y = 0, 0
                poseLM.append([x,y,z])
            
            pose = np.zeros((33,3))
            pose = np.array(poseLM)

        return img, pose

def main():
    cap = cv2.VideoCapture(0)
    pTime = 0
    detector = PoseDetector()
    while True:
        success, img = cap.read()
        img, faces = detector.findPose(img)
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
