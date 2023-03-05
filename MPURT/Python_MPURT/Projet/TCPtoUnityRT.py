import numpy as np
import socket


def sendData(position_array, clientSocket, sendNewLoadedPose = 0):
    # clientSocket.send((str(position_array.shape[0]) + " ").encode())
    # clientSocket.send((str(position_array.shape[1]) + " ").encode())
    # clientSocket.send((str(position_array.shape[2]) + " ").encode())
    
    #print(position_array)
    data = ""
    data = data + str('%.6f' % sendNewLoadedPose) + " "
    for i in range(position_array.shape[0]):
        for j in range(position_array.shape[1]):
                data = data + str('%.6f' % position_array[i][j]) + " "
    
    clientSocket.send(data.encode())
