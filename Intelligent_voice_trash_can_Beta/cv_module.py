from multiprocessing import Queue, Process
import threading
import cv2
import numpy as np
import time
import math
import onnxruntime

import os


import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMessageBox

# from open_camera import Ui_MainWindow
import numpy as np
import cv2
import time
from random import uniform
from PyQt5.Qt import *
import sys
import warnings
import threading
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QDateTime


# AImodel
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from torchvision import models
import torch.nn as nn
import torch
import os
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
import glob
from torch.utils.data import Dataset
import random
from PIL import ImageFile

import serial
import serial.tools.list_ports as serials

import copy


# 文件间的import
import AI_module_old
from lock import Lock

num0 = 0
# 用于初始化开机操作的参数
NN = 0
detect = 0

def edge_demo(image):
    edge_output = cv2.Canny(image, 50, 100)
    return edge_output


def detectSpam(frame, frame2,maskPath,frame2_valid=True):
    cv2.imwrite("img//frame.jpg", frame)
    global num0
    global detect
    # mask = cv2.imread(maskPath)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    rows1, cols1 = frame.shape
    # mask = mask[0:rows1, 0:cols1]
    # frame = cv2.bitwise_and(frame,frame,mask = mask)
    # dst = unevenLightCompensate(frame, 16)
    edge = edge_demo(frame)
    if edge.size != 0 : cv2.imwrite("img//edge1.jpg", edge)
    num1 = cv2.countNonZero(src=edge)

    # dst = unevenLightCompensate(frame2, 16)
    if frame2_valid == False:
        num2=0
    else:
        edge = edge_demo(frame2)
        if edge.size != 0 : cv2.imwrite("img//edge2.jpg", edge)
        num2 = cv2.countNonZero(src=edge)

    num = num1 + num2
    # print ('the number of NUM of the contour =%s'%(num))
    # print ('the number of NUM0 of the contour =%s'%(num0))
    if num0 == 0:
        num0 = num
    delta = num
    print("contour =%s" % (delta))
    if delta > 7000:
        #print('contour =%s'%(delta))
        num0 = num
        detect = detect + 1
        if detect >= 3:
            detect = 0
            return True
        else:
            return False
    else:
        num0 = num
        detect = 0
        return False


class Vision_Module:
    def __init__(
        self,
        q,#UI消息队列
        AI_module,
        voice_assistant_communication_queue,#语音助手消息队列
        cameraPath=0,
        cameraPath2=None,
        maskPath="img//mask.jpg",
        baud_rate=9600,#嵌入式传输波特率
        timeout=0.5,# 0.5秒连接超时
        serial_port_address="/dev/ttyUSB0",#串口位置
    ):
        self.ser=serial.Serial('/dev/ttyUSB0',9600,timeout=timeout)
        #self.ser.open()
        self.voice_assistant_communication_queue=voice_assistant_communication_queue
        self.cameraPath=cameraPath
        self.cameraPath2=cameraPath2
        if serial_port_address != None : self.ser = serial.Serial(serial_port_address, baudrate=baud_rate, timeout=0.5)
        self.detect = 0
        self.if20s = True#如果还在旋转验满的话，那么就不能进行检测，如果在验满就是false，不在这个状态就是true
        self.frame = None
        self.frame2 = None
        self.camera_path = cameraPath
        self.cap = cv2.VideoCapture(cameraPath)
        if cameraPath2!=None :self.cap2 = cv2.VideoCapture(cameraPath2)
        else : self.cap2=None
        self.ifGarbage = False
        self.frameOut = None
        self.garbageType = None
        self.totalNum = 0
        self.ifSuccess = False
        self.ifCompress = False
        self.fullLoad = False
        self.kitchen_Waste = 0
        self.recyclable_Trash = 0
        self.hazardous_Waste = 0
        self.other_Garbage = 0  
        self.trigger = False#是否在进行分类，如果是在进行分类，那么就阻塞countdown20s验满功能，在进行分类就是true，分完了就是false
        self.iftrigger = True#20s旋转验满功能开关，true就是开，false就是关
        self.qUIinformation = {
            "garbageCategory": None,
            "fullLoad": False,
            "ifSuccess": False,
            "TotalNumber": 0,
            "Kitchen waste": 0,
            "recyclable trash": 0,
            "hazardous waste": 0,
            "other garbage": 0,
            "serialOfGarbage": None,
            "ifBegin": False,
            "fullLoadGarbage": None,
            "fullLoadGarbage20s": False,
            "countDown": 0,
        }
        self.UIq = q
        self.mask_path = maskPath
        self.AI_module = AI_module
        self.machine_running=False

    def get_information_now(self):
        return self.qUIinformation
    def get_information(self):
        if self.voice_assistant_communication_queue.full():
            self.voice_assistant_communication_queue.get()
        self.voice_assistant_communication_queue.put(self.qUIinformation)
    
    def voice_assistant_transfer(self):
        while(True):
            time.sleep(1)
            self.get_information()
            
    def camera(self):
        try:
            reg, self.frame = self.cap.read()
            cv2.imwrite("img//1.jpg", self.frame)
            if self.cap2 !=None : reg, self.frame2 = self.cap2.read()
            else : self.frame2 = None
        except Exception as e:
            print('error in cameta')

    def detectionModule(self):
        try:
            return self.AI_module()
        except Exception as e:
            print('error in detectionModule')
            return False

    def CVModule(self):
        self.qUIinformation["ifBegin"] = True
        self.qUIinformation["ifBegin"] = True
        self.qUIinformation["ifSuccess"] = False

    def AIModule(self):
        flag,num_garbage = self.AI_module.Module(self.frame)
        if flag is None:
            return False
        print("flag=" + str(flag))
        if flag == 0:
            self.garbageType = "其他垃圾"
            self.other_Garbage += num_garbage
        elif flag == 1:
            self.garbageType = "厨余垃圾"
            self.kitchen_Waste += num_garbage
        elif flag == 2:
            self.garbageType = "可回收垃圾"
            self.recyclable_Trash += num_garbage
        elif flag == 3:
            self.garbageType = "有害垃圾"
            self.hazardous_Waste += num_garbage
        else:
            return False
        self.qUIinformation["serialOfGarbage"] = flag
        self.qUIinformation["ifBegin"] = True
        self.qUIinformation["ifSuccess"] = True
        print("AIModule done")
        return True

    def UI_pass_parameters_1(self):
        Lock.write_acquire()
        self.qUIinformation["fullLoad"] = self.fullLoad
        self.qUIinformation["ifSuccess"] = self.ifSuccess = True
        self.qUIinformation["garbageCategory"] = self.garbageType
        self.qUIinformation["Kitchen waste"] = self.kitchen_Waste
        self.qUIinformation["recyclable trash"] = self.recyclable_Trash
        self.qUIinformation["hazardous waste"] = self.hazardous_Waste
        self.qUIinformation["other garbage"] = self.other_Garbage
        self.totalNum += 1
        self.qUIinformation["TotalNumber"] = self.totalNum
        self.UIq.put(self.qUIinformation)
        Lock.write_release()
        # print('UI pass 1 done')

    def sendSerialInformation(self):
        print("正在发送数据")

        data = [[0x2C], [0x12], [0x00], [0x5B]]
        if self.garbageType == "其他垃圾":
            data[2] = [0x00]
        elif self.garbageType == "厨余垃圾":
            data[2] = [0x01]
        elif self.garbageType == "可回收垃圾":
            data[2] = [0x02]
        elif self.garbageType == "有害垃圾":
            data[2] = [0x03]
        else:
            print("error")
            exit()
        for i in range(0, 4):
            data[i] = bytearray(data[i])
            time.sleep(0.1)
            print(data[i])
            self.ser.write(data[i])
        print("sendSerialInformation done")

    def determineCompress(self):
        print("determineCompress have done")

    def recv(self):
        while True:
            data = self.ser.read(1)
            print(data)
            if data == b"":
                continue
            else:
                break
        return data

    def waitingForSerial(self):
        data=[0x00,0x00,0x00,0x00,0x00,0x00,0x00]

        print('开始等待读取')
        for i in range(0,7):
            data[i]=self.recv()
            data[i]=int.from_bytes(data[i],byteorder='big')
            print(data[i])
            #data[i]=ser.read(1)
            #print(data[i])
            #data[i]=int.from_bytes(data[i],byteorder='big')
        print('读取完成')
        if data[0]==0x2c and data[1]==0x12:
            
            self.qUIinformation['fullLoadGarbage20s']=False
            self.qUIinformation['ifSuccess'] = True

           
            for i in range(0,7):
                print(data[i])

            if data[2]==0x00:
                self.fullLoad=False
                self.qUIinformation['fullLoad']=False
                if data[3]==0x00:
                    self.qUIinformation['fullLoadGarbage']=0
                elif data[3]==0x01:
                    self.qUIinformation['fullLoadGarbage']=1
                elif data[3]==0x02:
                    self.qUIinformation['fullLoadGarbage']=2
                elif data[3]==0x03:
                    self.qUIinformation['fullLoadGarbage']=3
                else:
                    self.qUIinformation['fullLoadGarbage']=None

            elif data[2]==0x01:
                self.fullLoad=True
                self.qUIinformation['fullLoad']=True
                if data[3]==0x00:
                    self.qUIinformation['fullLoadGarbage']=10
                elif data[3]==0x01:
                    self.qUIinformation['fullLoadGarbage']=11
                elif data[3]==0x02:
                    self.qUIinformation['fullLoadGarbage']=12
                elif data[3]==0x03:
                    self.qUIinformation['fullLoadGarbage']=13
                else:
                    self.qUIinformation['fullLoadGarbage']=None

            else:
                self.qUIinformation['fullLoadGarbage']=None
            return True



        #5D、30、2A数据包结构
        if data[0]== 0x5D and data[1]== 0x30:


            self.qUIinformation['fullLoadGarbage20s']=True
            self.qUIinformation['fullLoadGarbage']=[False,False,False,False]
            for i in range(0,7):
                print(data[i])

            if data[2]==True:
                self.qUIinformation['fullLoadGarbage'][0]=True
            else:
                self.qUIinformation['fullLoadGarbage'][0]=False
            if data[3]==True:
                self.qUIinformation['fullLoadGarbage'][1]=True
            else:
                self.qUIinformation['fullLoadGarbage'][1]=False
            if data[4]==True:
                self.qUIinformation['fullLoadGarbage'][2]=True
            else:
                self.qUIinformation['fullLoadGarbage'][2]=False
            if data[5]==True:
                self.qUIinformation['fullLoadGarbage'][3]=True
            else:
                self.qUIinformation['fullLoadGarbage'][3]=False
            self.if20s=True
            return True

        print('waitingForSerial have done')

    def UI_pass_parameters_2(self):
        self.qUIinformation["fullLoad"] = self.fullLoad
        self.qUIinformation["ifBegin"] = False
        self.UIq.put(self.qUIinformation)
        # print('UI pass 0 done')

    def UI_pass_parameters_0(self):
        self.qUIinformation["garbageCategory"] = None
        self.qUIinformation["Kitchen waste"] = self.kitchen_Waste
        self.qUIinformation["recyclable trash"] = self.recyclable_Trash
        self.qUIinformation["hazardous waste"] = self.hazardous_Waste
        self.qUIinformation["other garbage"] = self.other_Garbage
        self.qUIinformation["ifSuccess"] = self.ifSuccess = False
        self.qUIinformation["TotalNumber"] = self.totalNum
        self.qUIinformation["fullLoad"] = self.fullLoad

        self.UIq.put(self.qUIinformation)
        # print('UI pass 0 done')

    def UI_pass_parameters_3(self):
        print("UI_pass_parameters_3 开始")
        while (
            self.qUIinformation["ifBegin"] == True
            and self.qUIinformation["ifSuccess"] == False
        ):
            self.qUIinformation["garbageCategory"] = None
            self.qUIinformation["Kitchen waste"] = self.kitchen_Waste
            self.qUIinformation["recyclable trash"] = self.recyclable_Trash
            self.qUIinformation["hazardous waste"] = self.hazardous_Waste
            self.qUIinformation["other garbage"] = self.other_Garbage
            self.qUIinformation["TotalNumber"] = self.totalNum
            self.qUIinformation["fullLoad"] = self.fullLoad

            self.UIq.put(self.qUIinformation)

        # print('UI pass 3 done')

    def UI_pass_parameters_4(self):
        # print('UI_pass_parameters_4 开始')

        while (
            self.qUIinformation["ifBegin"] == True
            and self.qUIinformation["ifSuccess"] == True
        ):
            self.qUIinformation["garbageCategory"] = self.garbageType
            self.qUIinformation["Kitchen waste"] = self.kitchen_Waste
            self.qUIinformation["recyclable trash"] = self.recyclable_Trash
            self.qUIinformation["hazardous waste"] = self.hazardous_Waste
            self.qUIinformation["other garbage"] = self.other_Garbage
            self.qUIinformation["TotalNumber"] = self.totalNum
            self.UIq.put(self.qUIinformation)

        # print('UI pass 4 done')

    def countDown(self):
        while True:
            i = 0
            if self.iftrigger:
                for i in range(0, 20):
                    time.sleep(1)
                    self.qUIinformation["countDown"] = i + 1
                    if self.trigger:
                        # 阻塞（规范代码应该写专门的阻塞函数，后续需要优化）
                        while self.trigger:
                            a = 10  # 优化
                        self.trigger = False
                        break
                if not self.trigger and i == 19:
                    self.if20s = False
                    self.machine_running=True
                    self.sendSerialOfTrigger()
                    self.waitingForSerial()
                    self.machine_running=False

    def sendSerialOfTrigger(self):
        data = [[0x5D], [0x30], [0x01], [0x2A]]
        for i in range(0, 4):
            data[i] = bytearray(data[i])
            print(data[i])
            time.sleep(0.1)
            self.ser.write(data[i])

        print("sendSerialOfTrigger has done")
        self.trigger = False
        self.iftrigger = False

    def run(self):
        global NN
        global detect
        # 一定时间检测满载情况线程
        t0 = threading.Thread(target=self.countDown, args=())
        t0.start()
        # 进行传输给语音助手的线程
        #voice_assistant_transfer_thread = threading.Thread(target=self.voice_assistant_transfer,args=())
        #voice_assistant_transfer_thread.start()

        while True:
            try:
                self.cap.open(self.cameraPath)
                if self.cameraPath2 != None: self.cap2.open(self.cameraPath2)
                self.camera()
            except Exception as e:
                print("camera can't open")
                continue
            if not self.detectionModule():
                self.UI_pass_parameters_0()
            elif self.if20s:
                detect = -1
                NN = NN + 1
                self.cap.release()
                if self.cap2 != None :self.cap2.release()
                self.trigger = True
                # time.sleep(0.5)
                self.cap.open(0)

                self.camera()
                self.cap.release()

                t1 = threading.Thread(target=self.UI_pass_parameters_3, args=())
                t2 = threading.Thread(target=self.UI_pass_parameters_4, args=())

                self.CVModule()
                t1.start()
                # self.AIModule()
                self.UI_pass_parameters_1()

                t2.start()
                self.machine_running=True
                self.sendSerialInformation()
                try:
                    if self.waitingForSerial():
                        self.UI_pass_parameters_2()
                except:
                    self.fullLoad = False
                    self.qUIinformation["fullLoad"] = False
                    self.qUIinformation["ifBegin"] = False
                    self.qUIinformation["ifSuccess"] = True
                self.machine_running=False
                self.fullLoad = False
                self.trigger = False
                self.iftrigger = True
                if NN == 0:
                    self.frame = None
                    self.cap = cv2.VideoCapture(self.cameraPath)
                    self.ifGarbage = False
                    self.frameOut = None
                    self.garbageType = None
                    self.totalNum = 0
                    self.ifSuccess = False
                    self.ifCompress = False
                    self.fullLoad = False
                    self.kitchen_Waste = 0
                    self.recyclable_Trash = 0
                    self.hazardous_Waste = 0
                    self.other_Garbage = 0
                    self.trigger = False
                    self.iftrigger = True
                    self.qUIinformation = {
                        "garbageCategory": None,
                        "fullLoad": False,
                        "ifSuccess": False,
                        "TotalNumber": 0,
                        "Kitchen waste": 0,
                        "recyclable trash": 0,
                        "hazardous waste": 0,
                        "other garbage": 0,
                        "serialOfGarbage": None,
                        "ifBegin": False,
                        "fullLoadGarbage": None,
                        "fullLoadGarbage20s": False,
                        "countDown": 0,
                    }

                else:
                    continue
