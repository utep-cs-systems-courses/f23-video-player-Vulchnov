#!/usr/bin/env python3

from threading import *
import cv2
import numpy as np
import base64
import queue
import os.path

class q:
    def __init__(self):
        self.storage = []
        self.StorageLock = Lock()
        self.Full = Semaphore(0)
        self.Empty = Semaphore(30)

    def insert(self, item):
        self.Empty.acquire()
        self.StorageLock.acquire()
        self.storage.append(item)
        self.StorageLock.release()
        self.Full.release()

    def remove(self):
        self.Full.acquire()
        self.StorageLock.acquire()
        item = self.storage.pop()
        self.StorageLock.release()
        self.Empty.release()
        return item
frameNum = 1000

def producer(Que: q, clipFileName):
    vidcap = cv2.VideoCapture(clipFileName)
    global frameNum
    frameNum = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    for i in range(frameNum):
        success,image = vidcap.read()
        Que.insert(image)


def grayScale(Que1: q, Que2: q):
    global frameNum
    frame = Que1.remove()
    for i in range(frameNum-1):
        grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        Que2.insert(grayscaleFrame)
        frame = Que1.remove()
    grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    Que2.insert(grayscaleFrame)


def consumer(Que: q):
    global frameNum
    frame = Que.remove()
    for i in range(frameNum-1):
        cv2.imshow('Video', frame)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break
        frame = Que.remove()
    cv2.imshow('Video', frame)
    cv2.destroyAllWindows()

Que1 = q()
Que2 = q()

inputs = ""

while 1:
    
    inputs = input("What video clip\n")
    if(inputs == "q"):
        break

    if(os.path.isfile(inputs)):
        t1 = Thread(target=producer, args=(Que1, inputs,))
        t2  = Thread(target=grayScale, args=(Que1, Que2,))
        t3 = Thread(target=consumer, args=(Que2,))
            

        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()

    else:
        print("That file does not exist\n")