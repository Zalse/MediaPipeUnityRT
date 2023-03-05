import FaceMeshModule
import PoseModule
import cv2

# Open the webcam
cam = cv2.VideoCapture(0)

# Loop until the user hits the 'q' key
while True:
    # Read a frame from the webcam
    _, frame = cam.read()

    detector = FaceMeshModule.FaceMeshDetector(refineLM=True)

    frame, _ = detector.findFaceMesh(frame)

    # Display the frame in a window
    cv2.imshow("Webcam", frame)

    # Check if the user pressed the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cam.release()
cv2.destroyAllWindows()
