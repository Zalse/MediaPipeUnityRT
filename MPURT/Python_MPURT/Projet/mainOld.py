import threading
import time
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
import videoTreatment

class WebcamVideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = threading.Lock()

    def start(self):
        if self.started:
            print("already started!!")
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            (grabbed, frame) = self.stream.read()
            self.read_lock.acquire()
            self.grabbed, self.frame = grabbed, frame
            self.read_lock.release()

    def read(self):
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.stream.release()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        #My code
        self.saved_pose = np.zeros((33,2))
        self.current_pos = np.zeros((33,2))
        self.videoTreatment = videoTreatment.VideoTraitement()
        self.pTime = 0
        self.isDisplayFPS = True

        #Add Buttons
        self.start_button = QtWidgets.QPushButton('Start')
        self.stop_button = QtWidgets.QPushButton('Stop')
        self.save_pose_button = QtWidgets.QPushButton('Save Pose')
        self.fpsCheckbox = QtWidgets.QCheckBox('Display FPS')
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.save_pose_button)
        self.layout.addWidget(self.fpsCheckbox)

        #Connect the buttons to functions
        self.start_button.clicked.connect(self.start_stream)
        self.stop_button.clicked.connect(self.stop_stream)
        self.save_pose_button.clicked.connect(self.save_current_pose)

        # create a label to display the webcam stream
        self.label = QtWidgets.QLabel()
        self.label.setFixedSize(960, 720)

        # add the label to the layout
        self.layout.addWidget(self.label)

        # start the webcam stream
        self.cap = WebcamVideoStream().start()

        # create a timer to update the webcam stream every 10ms
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

    def update_fps(self, frame):
        if(self.fpsCheckbox.isChecked()):
            cTime = time.time()
            fps = 1 / (cTime - self.pTime)
            self.pTime = cTime
            cv2.putText(frame, str(int(fps)), (20, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, (0, 0, 0), 3)

    def start_stream(self):
        self.cap = WebcamVideoStream().start()
        self.timer.start(10)

    def stop_stream(self):
        self.timer.stop()
        self.cap.stop()

    def save_current_pose(self):
        print("save pose")
        self.saved_pose = self.current_pos


    def update_frame(self):

        if self.cap.started:
            # get the current frame from the webcam
            frame = self.cap.read()
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)

            self.update_fps(frame)

            frame, poseLM = self.videoTreatment.treatment(frame, saved_pose=self.saved_pose, current_pose=self.current_pos)
            self.current_pos = poseLM
            # convert the frame to a QImage and display it in the label
            img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pix = QPixmap.fromImage(img)
            self.label.setPixmap(pix)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
