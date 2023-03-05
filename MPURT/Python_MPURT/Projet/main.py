import math
import time
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtGui import QImage, QPixmap, QColor
import videoTreatment
import socket
import TCPtoUnityRT as toUnity


class VideoStream:
    def __init__(self, src = 0):
        self.stream = cv2.VideoCapture(src)
        self.started = True

    def stop(self):
        self.stream.release()
        self.started = False

    def start(self, src = 0):
        self.stream = cv2.VideoCapture(src)
        self.started = True

    def read(self):
        _, frame = self.stream.read()
        return frame

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        # My code
        self.listPoses = np.empty((0, 33, 2), dtype=np.float64)
        self.loadedPoses = np.load("ListPose.npy")
        print("Loaded " + str(self.loadedPoses.shape[0]) + " poses")
        self.pTime = 0
        self.isDisplayFPS = True
        self.maskColor = (0,0,0)
        self.saved_pose = self.loadedPoses[0]
        self.current_pos = np.zeros((33,2))
        self.videoTreatment = videoTreatment.VideoTraitement()
        self.isConnectedToUnity = False
        self.sendLoadedPose = True

        # Create utility Buttons
        self.start_button = QtWidgets.QPushButton('Restart video')
        self.stop_button = QtWidgets.QPushButton('Stop video')
        self.cameraSelector = QtWidgets.QSpinBox()
        self.fpsCheckbox = QtWidgets.QCheckBox('Display FPS')
        self.cameraSelector.setMinimum(0)
        # TODO implement a function that get the number of cameras
        self.cameraSelector.setMaximum(3)
        self.connect_unity_button = QtWidgets.QPushButton('Connect to Unity')

        # Create pose buttons
        self.save_pose_button = QtWidgets.QPushButton('Save Pose')        
        self.load_pose_button = QtWidgets.QPushButton('Load pose')        
        self.poseSelector = QtWidgets.QSpinBox()
        self.poseSelector.setMinimum(1)
        self.poseSelector.setMaximum(self.loadedPoses.shape[0])

        # create horizontal layouts to hold the buttons
        self.utility_layout = QtWidgets.QHBoxLayout()
        self.pose_layout = QtWidgets.QHBoxLayout()

        # add the utility buttons to the layout
        self.utility_layout.addWidget(self.start_button)
        self.utility_layout.addWidget(self.stop_button)
        self.utility_layout.addWidget(self.fpsCheckbox)
        self.utility_layout.addWidget(self.cameraSelector)
        self.utility_layout.addWidget(self.connect_unity_button)

        # Add the pose buttons to the layout
        self.pose_layout.addWidget(self.save_pose_button)
        self.pose_layout.addWidget(self.poseSelector)
        self.pose_layout.addWidget(self.load_pose_button)

        # add the horizontal layout to the main layout
        self.layout.addLayout(self.utility_layout)
        self.layout.addLayout(self.pose_layout)

        #Connect the utility buttons to functions
        self.start_button.clicked.connect(self.start_stream)
        self.stop_button.clicked.connect(self.stop_stream)
        self.cameraSelector.valueChanged.connect(self.changeCam)
        self.connect_unity_button.clicked.connect(self.connectToUnity)

        #Connect the pose buttons to functions
        self.save_pose_button.clicked.connect(self.save_current_pose)
        self.load_pose_button.clicked.connect(self.load_chosen_pose)

        # Create a label to hold the video
        self.label = QtWidgets.QLabel()

        # add the label to the layout
        self.layout.addWidget(self.label)

        # start the webcam stream
        self.videoStream = VideoStream()

        # set the size of the window
        self.label.setFixedSize(self.videoStream.read().shape[1], self.videoStream.read().shape[0])

        # create a timer to update the webcam stream every 10ms
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

    def changeCam(self):
        self.videoStream.stop()
        self.videoStream.start(self.cameraSelector.value())
        self.label.setFixedSize(self.videoStream.read().shape[1], self.videoStream.read().shape[0])

    def update_fps(self, frame):
        if(self.fpsCheckbox.isChecked()):
            cTime = time.time()
            fps = 1 / (cTime - self.pTime)
            self.pTime = cTime
            cv2.putText(frame, str(int(fps)), (20, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, (255, 255, 255), 3)

    def start_stream(self):
        self.videoStream.start()
        self.timer.start(10)

    def stop_stream(self):
        self.timer.stop()
        self.videoStream.stop()

    def save_current_pose(self):
        print("save pose")
        self.saved_pose = self.current_pos
        self.listPoses = np.append(self.listPoses, [self.saved_pose], axis=0)
        np.save("poseTest.npy", self.listPoses)    
        #print(self.listPoses.shape) 
        #self.poseSelector.setValue(1)
    
    def load_chosen_pose(self):
        print("Load pose number : " + str(self.poseSelector.value()))
        self.saved_pose = self.loadedPoses[self.poseSelector.value() - 1]

    def checkIfGood(self):
        if (self.videoTreatment.isAllGood == True):
            print("All good ! Load next pose !")
            if (self.poseSelector.value() == self.loadedPoses.shape[0]):
                self.poseSelector.setValue(1)
            else:
                self.poseSelector.setValue(self.poseSelector.value() + 1)
            self.saved_pose = self.loadedPoses[self.poseSelector.value() - 1]
            self.sendLoadedPose = True
        else:
            self.sendLoadedPose = False
        
    
    def connectToUnity(self):
        print("Connection to Unity...")
        try:
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientSocket.connect(('127.0.0.1', 5500))
            self.clientSocket.setblocking(0)

        except Exception:
            print("Connection Failure, you may have not started unity properly")
            return

        self.isConnectedToUnity = True
        print("Connection successful")

    

    def update_frame(self):
        if self.videoStream.started:
            # get the current frame from the webcam
            frame = self.videoStream.read()
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)

            frame, poseLM = self.videoTreatment.treatment(frame, saved_pose=self.saved_pose, current_pose=self.current_pos)

            if (self.isConnectedToUnity == True):
                if(self.sendLoadedPose):
                    print("Send Loaded pose")
                    savedPose3D = np.hstack((self.saved_pose, np.zeros((self.saved_pose.shape[0],1))))
                    toUnity.sendData(savedPose3D, self.clientSocket, 1)
                else:
                    toUnity.sendData(poseLM, self.clientSocket)                   
            

            self.current_pos = (np.delete(poseLM, 2, axis=1))

            self.checkIfGood()

            self.update_fps(frame)
            # convert the frame to a QImage and display it in the label
            img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pix = QPixmap.fromImage(img)
            self.label.setPixmap(pix)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()