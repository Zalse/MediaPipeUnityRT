import array

import cv2
import mediapipe as mp
import time

class FaceMeshDetector:

    def __init__(self, staticMode = False, maxFaces = 2, refineLM = False, minDetConf = 0.5 , minTrackConf = 0.5):
        self.staticMode = staticMode
        self.maxFaces = maxFaces
        self.refineLM = refineLM
        self.minDetConf = minDetConf
        self.minTrackConf = minTrackConf
        self.mpDraw = mp.solutions.drawing_utils
        self.mpFacemesh = mp.solutions.face_mesh
        self.faceMesh = self.mpFacemesh.FaceMesh(self.staticMode,self.maxFaces,self.refineLM,self.minDetConf,self.minTrackConf)
        self.drawSpec = self.mpDraw.DrawingSpec(thickness=2, circle_radius=2,color=(0,255,0))

    def findFaceMesh(self, img, draw = True):
        self.imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.faceMesh.process(self.imgRGB)
        faces = []
        if self.results.multi_face_landmarks :
            for faceLM in self.results.multi_face_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, faceLM, self.mpFacemesh.FACEMESH_LIPS, landmark_drawing_spec=self.drawSpec)
            face =  []
            for id,lm in enumerate(faceLM.landmark) :
                #print(lm)
                ih, iw, ic = img.shape
                x, y = int(lm.x * iw), int(lm.y * ih)
                #print(id,x,y)
                face.append([x,y])
            faces.append(face)
        return img, faces


def main():
    cap = cv2.VideoCapture(0)
    pTime = 0
    detector = FaceMeshDetector(refineLM=True)
    while True:
        success, img = cap.read()
        img, faces = detector.findFaceMesh(img)
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