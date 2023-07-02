from multiprocessing import Queue, Process
import threading
import cv2
import numpy as np
import time
import math
import onnxruntime
import copy
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


class showUI(QtWidgets.QMainWindow):
    def __init__(self, UIQ):
        super().__init__()
        self.initUI()
        self.flag = False
        self.img = None
        self.UIflag = 0
        self.UIQ = UIQ

    def initUI(self):
        desktop = QApplication.desktop()

        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setBold(True)
        font.setPointSize(20)
        font.setWeight(100)

        self.main_widget = QtWidgets.QWidget()  # 创建窗口主部件
        self.main_layout = QtWidgets.QGridLayout()  # 创建主部件的网格布局
        self.main_widget.setLayout(self.main_layout)  # 设置窗口主部件布局为网格布局

        ###########上面的部件#######
        self.On_widget = QtWidgets.QWidget()
        self.On_widget.setObjectName("On_widget")
        self.On_layout = QtWidgets.QGridLayout()
        self.On_widget.setLayout(self.On_layout)
        self.On_widget.setStyleSheet(
            """QWidget{border-radius:7px;background-color:#ee0000;}"""
        )
        ##########中间的部件##############
        self.Md_widget = QtWidgets.QWidget()
        self.Md_widget.setObjectName("Md_widget")
        self.Md_layout = QtWidgets.QGridLayout()
        self.Md_widget.setLayout(self.Md_layout)
        self.Md_widget.setStyleSheet(
            """QWidget{border-radius:7px;background-color:#66FFCC;}"""
        )
        ############下面的步见################
        self.Dn_widget = QtWidgets.QWidget()
        self.Dn_widget.setObjectName("Dn_widget")
        self.Dn_layout = QtWidgets.QGridLayout()
        self.Dn_widget.setLayout(self.Dn_layout)
        self.Dn_widget.setStyleSheet(
            """QWidget{border-radius:7px;background-color:#28B464;}"""
        )

        self.main_layout.addWidget(self.On_widget, 0, 6, 2, 5)
        self.main_layout.addWidget(self.Md_widget, 3, 6, 8, 5)
        self.main_layout.addWidget(self.Dn_widget, 12, 6, 4, 5)

        self.setCentralWidget(self.main_widget)  # 设置窗口主部件
        self.main_widget.setStyleSheet(
            """QWidget{border-radius:7px;background-color:#66CCFF;}"""
        )

        self.label_0 = QtWidgets.QLabel(self)  # 用来显示垃圾类别
        self.label_0.setFont(font)
        self.label_0.resize(desktop.width() * 0.4, desktop.height() * 0.1)
        self.label_0.move(desktop.width() * 0.85, desktop.height() * 0.00)

        self.label_1 = QtWidgets.QLabel(self)  # 用来显示可回收垃圾
        self.label_1.setFont(font)
        self.label_1.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_1.move(desktop.width() * 0.67, desktop.height() * 0.1)

        self.label_2 = QtWidgets.QLabel(self)  # 用来显示厨余垃圾
        self.label_2.setFont(font)
        self.label_2.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_2.move(desktop.width() * 0.67, desktop.height() * 0.23)

        self.label_3 = QtWidgets.QLabel(self)  # 用来显示其他垃圾
        self.label_3.setFont(font)
        self.label_3.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_3.move(desktop.width() * 0.67, desktop.height() * 0.49)

        self.label_13 = QtWidgets.QLabel(self)  # 用来显示有害垃圾
        self.label_13.setFont(font)
        self.label_13.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_13.move(desktop.width() * 0.67, desktop.height() * 0.36)

        self.label_4 = QtWidgets.QLabel(self)  # 用来显示是否完成分类
        self.label_4.setFont(font)
        self.label_4.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_4.move(desktop.width() * 0.7, desktop.height() * 0.62)

        self.label_5 = QtWidgets.QLabel(self)  # 用来显示success or false
        self.label_5.setFont(font)
        self.label_5.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_5.move(desktop.width() * 0.9, desktop.height() * 0.62)

        self.label_6 = QtWidgets.QLabel(self)  # 用来显示是否满载
        self.label_6.setFont(font)
        self.label_6.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_6.move(desktop.width() * 0.7, desktop.height() * 0.75)

        self.label_7 = QtWidgets.QLabel(self)  # 用来显示满载true or false
        self.label_7.setFont(font)
        self.label_7.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_7.move(desktop.width() * 0.9, desktop.height() * 0.75)

        self.label_8 = QtWidgets.QLabel(self)  # 用来显示所有垃圾总数
        self.label_8.setFont(font)
        self.label_8.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_8.move(desktop.width() * 0.76, desktop.height() * 0.015)

        self.label_8_1 = QtWidgets.QLabel(self)  # 用来显示 序号
        self.label_8_1.setFont(font)
        self.label_8_1.resize(desktop.width() * 0.4, desktop.height() * 0.1)
        self.label_8_1.move(desktop.width() * 0.75, desktop.height() * 0.0)

        self.label_9 = QtWidgets.QLabel(self)  # 用来显示可回收垃圾总数
        self.label_9.setFont(font)
        self.label_9.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_9.move(desktop.width() * 0.83, desktop.height() * 0.1)

        self.label_10 = QtWidgets.QLabel(self)  # 用来显示厨余垃圾总数
        self.label_10.setFont(font)
        self.label_10.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_10.move(desktop.width() * 0.83, desktop.height() * 0.23)

        self.label_11 = QtWidgets.QLabel(self)  # 用来显示有害垃圾总数
        self.label_11.setFont(font)
        self.label_11.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_11.move(desktop.width() * 0.83, desktop.height() * 0.36)

        self.label_12 = QtWidgets.QLabel(self)  # 用来显示其他垃圾总数
        self.label_12.setFont(font)
        self.label_12.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_12.move(desktop.width() * 0.83, desktop.height() * 0.49)

        #####显示是否满载############
        self.label_9f = QtWidgets.QLabel(self)  # 用来显示可回收垃圾是否满载
        self.label_9f.setFont(font)
        self.label_9f.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_9f.move(desktop.width() * 0.9, desktop.height() * 0.1)

        self.label_10f = QtWidgets.QLabel(self)  # 用来显示厨余垃圾是否满载
        self.label_10f.setFont(font)
        self.label_10f.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_10f.move(desktop.width() * 0.9, desktop.height() * 0.23)

        self.label_11f = QtWidgets.QLabel(self)  # 用来显示有害垃圾是否满载
        self.label_11f.setFont(font)
        self.label_11f.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_11f.move(desktop.width() * 0.9, desktop.height() * 0.36)

        self.label_12f = QtWidgets.QLabel(self)  # 用来显示其他垃圾是否满载
        self.label_12f.setFont(font)
        self.label_12f.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_12f.move(desktop.width() * 0.9, desktop.height() * 0.49)

        self.label_14 = QtWidgets.QLabel(self)  # 用来显示 垃圾的类别
        self.label_14.setFont(font)
        self.label_14.resize(desktop.width() * 0.4, desktop.height() * 0.2)
        self.label_14.move(desktop.width() * 0.85, desktop.height() * 0.01)

        self.label_15 = QtWidgets.QLabel(self)  # 用来显示视频
        self.label_15.resize(desktop.width() * 0.65, desktop.height() * 0.65)
        self.label_15.move(desktop.width() * 0.0, desktop.height() * 0.00)

        self.label_16 = QtWidgets.QLabel(self)  # 用来显示是否完成的图像
        self.label_16.resize(desktop.width() * 0.50, desktop.height() * 0.65)
        self.label_16.move(desktop.width() * 0.00, desktop.height() * 0.49)

        self.label_17 = QtWidgets.QLabel(self)  # 用来显示垃圾种类的图像
        self.label_17.resize(desktop.width() * 0.3, desktop.height() * 0.3)
        self.label_17.move(desktop.width() * 0.50, desktop.height() * 0.665)

        self.label_18 = QtWidgets.QLabel(self)  # 用来显示“倒计时”
        self.label_18.setFont(font)
        self.label_18.resize(desktop.width() * 0.4, desktop.height() * 0.1)
        self.label_18.move(desktop.width() * 0.665, desktop.height() * 0.0)

        self.label_19 = QtWidgets.QLabel(self)  # 用来显示倒计时数字
        self.label_19.setFont(font)
        self.label_19.resize(desktop.width() * 0.4, desktop.height() * 0.1)
        self.label_19.move(desktop.width() * 0.68, desktop.height() * 0.05)

        self.label_20 = QtWidgets.QLabel(self)  # 显示小格式序号
        self.label_20.resize(desktop.width() * 0.2, desktop.height() * 0.1)
        self.label_20.move(desktop.width() * 0.7, desktop.height() * 0.75)

        self.label_21 = QtWidgets.QLabel(self)  # 显示小格式垃圾种类
        self.label_21.resize(desktop.width() * 0.2, desktop.height() * 0.1)
        self.label_21.move(desktop.width() * 0.7, desktop.height() * 0.78)

        self.label_22 = QtWidgets.QLabel(self)  # 显示小格式数量
        self.label_22.resize(desktop.width() * 0.2, desktop.height() * 0.1)
        self.label_22.move(desktop.width() * 0.7, desktop.height() * 0.81)

        self.label_23 = QtWidgets.QLabel(self)  # 显示小格式分类成功与否
        self.label_23.resize(desktop.width() * 0.2, desktop.height() * 0.1)
        self.label_23.move(desktop.width() * 0.7, desktop.height() * 0.85)

        self.label_24 = QtWidgets.QLabel(self)  # 显示  总数
        self.label_24.resize(desktop.width() * 0.2, desktop.height() * 0.1)
        self.label_24.move(desktop.width() * 0.82, desktop.height() * 0.76)

        self.label_25 = QtWidgets.QLabel(self)  # 显示小格式 垃圾种类
        self.label_25.resize(desktop.width() * 0.2, desktop.height() * 0.1)
        self.label_25.move(desktop.width() * 0.82, desktop.height() * 0.79)

        self.label_26 = QtWidgets.QLabel(self)  # 显示小格式 同种数量
        self.label_26.resize(desktop.width() * 0.2, desktop.height() * 0.1)
        self.label_26.move(desktop.width() * 0.82, desktop.height() * 0.82)

        self.label_27 = QtWidgets.QLabel(self)  # 显示小格式 分类成功与否
        self.label_27.resize(desktop.width() * 0.2, desktop.height() * 0.1)
        self.label_27.move(desktop.width() * 0.82, desktop.height() * 0.86)

        self.setWindowTitle("垃圾桶工作状态")
        self.setGeometry(600, 600, 1000, 500)
        self.showMaximized()

    def setupUi(self):
        self.Timer1 = QTimer()  # 自定义QTimer
        showVideoThread = threading.Thread(target=self.getImg)  # 播放视频
        showVideoThread.setDaemon(True)
        showVideoThread.start()
        self.Timer1.start(0.035)  # 每0.035秒运行一次
        time.sleep(0.1)
        self.Timer1.timeout.connect(self.showVideo)
        self.Timer1.timeout.connect(self.update)  # 连接update
        self.Timer1.timeout.connect(self.showImage)
        self.Timer1.timeout.connect(self.showImage_2)
        QtCore.QMetaObject.connectSlotsByName(self)

    def yunUI1(self):
        img = cv2.imread("img//g.png")
        cv2.imwrite("img//4.png", img)
        img = cv2.imread("img//a.png")
        cv2.imwrite("img//5.png", img)

    def yunUI2(self):
        img = cv2.imread("img//2.png")
        cv2.imwrite("img//4.png", img)
        if self.UIflag >= 0 and self.UIflag <= 10:
            img = cv2.imread("img//h1.png")
            self.UIflag += 1
        elif self.UIflag > 10 and self.UIflag <= 20:
            img = cv2.imread("img//h2.png")
            self.UIflag += 1

        elif self.UIflag > 20 and self.UIflag <= 30:
            img = cv2.imread("img//h3.png")
            self.UIflag += 1

        elif self.UIflag > 30 and self.UIflag <= 40:
            img = cv2.imread("img//h4.png")
            self.UIflag += 1
        else:
            img = cv2.imread("img//h4.png")
            self.UIflag -= 41
        cv2.imwrite("img//5.png", img)

    def yunUI3(self):
        img = cv2.imread("img//3.png")
        cv2.imwrite("img//4.png", img)
        if self.UIinformation["serialOfGarbage"] == 1:
            img = cv2.imread("img//b.png")
        elif self.UIinformation["serialOfGarbage"] == 3:
            img = cv2.imread("img//c.png")
        elif self.UIinformation["serialOfGarbage"] == 2:
            img = cv2.imread("img//d.png")
        else:
            img = cv2.imread("img//e.png")
        cv2.imwrite("img//5.png", img)

    def update(self):
        print("the UIQ is ready to get")
        self.UIinformation = self.UIQ.get()
        print("the information is get")
        if (
            self.UIinformation["ifBegin"] == False
            and self.UIinformation["ifSuccess"] == False
        ):
            self.yunUI1()
        elif (
            self.UIinformation["ifBegin"] == True
            and self.UIinformation["ifSuccess"] == False
        ):
            self.yunUI2()
        elif (
            self.UIinformation["ifBegin"] == True
            and self.UIinformation["ifSuccess"] == True
        ):
            self.yunUI3()

        self.label_0.setText("垃圾种类")
        self.label_1.setText("可回收垃圾")
        self.label_2.setText("厨余垃圾")
        self.label_3.setText("其他垃圾")
        self.label_4.setText("分类成功与否")
        if self.UIinformation["ifSuccess"]:
            self.label_5.setText("OK!")
        else:
            self.label_5.setText("不OK!")

        # self.label_5.setText(str(self.UIinformation['ifSuccess']))
        # self.label_6.setText('是否满载')
        # self.label_7.setText(str(self.UIinformation['fullLoad']))
        self.label_8.setText(str(self.UIinformation["TotalNumber"]))
        self.label_8_1.setText("序号")
        self.label_9.setText(str(self.UIinformation["recyclable trash"]))
        self.label_10.setText(str(self.UIinformation["Kitchen waste"]))
        self.label_11.setText(str(self.UIinformation["hazardous waste"]))
        self.label_12.setText(str(self.UIinformation["other garbage"]))
        self.label_13.setText("有害垃圾")
        self.label_14.setText(self.UIinformation["garbageCategory"])
        self.label_18.setText("倒计时")
        self.label_19.setText(str(20 - self.UIinformation["countDown"]))

        self.label_20.setText("序号")
        self.label_21.setText("垃圾种类")
        self.label_22.setText("数量")
        self.label_23.setText("分类成功与否")

        if self.UIinformation["ifSuccess"]:
            self.label_24.setText(str(self.UIinformation["TotalNumber"]))
            self.label_25.setText(self.UIinformation["garbageCategory"])

            if self.UIinformation["garbageCategory"] == "可回收垃圾":
                self.label_26.setText(str(self.UIinformation["recyclable trash"]))
            elif self.UIinformation["garbageCategory"] == "厨余垃圾":
                self.label_26.setText(str(self.UIinformation["Kitchen waste"]))
            elif self.UIinformation["garbageCategory"] == "有害垃圾":
                self.label_26.setText(str(self.UIinformation["hazardous waste"]))
            elif self.UIinformation["garbageCategory"] == "其他垃圾":
                self.label_26.setText(str(self.UIinformation["other garbage"]))
        else:
            self.label_24.setText("")
            self.label_25.setText("")
            self.label_26.setText("")

        if self.UIinformation["ifSuccess"]:
            self.label_27.setText("OK!")
        else:
            self.label_27.setText("不OK!")

        if not self.UIinformation["fullLoadGarbage20s"]:
            if self.UIinformation["fullLoadGarbage"] == None:
                a = 0

            elif self.UIinformation["fullLoadGarbage"] == 2:
                self.label_9f.setText("未满载")

            elif self.UIinformation["fullLoadGarbage"] == 1:
                self.label_10f.setText("未满载")

            elif self.UIinformation["fullLoadGarbage"] == 3:
                self.label_11f.setText("未满载")

            elif self.UIinformation["fullLoadGarbage"] == 0:
                self.label_12f.setText("未满载")

            elif self.UIinformation["fullLoadGarbage"] == 12:
                self.label_9f.setText("满载")

            elif self.UIinformation["fullLoadGarbage"] == 11:
                self.label_10f.setText("满载")

            elif self.UIinformation["fullLoadGarbage"] == 13:
                self.label_11f.setText("满载")

            elif self.UIinformation["fullLoadGarbage"] == 10:
                self.label_12f.setText("满载")

        else:
            if self.UIinformation["fullLoadGarbage"][2] == True:
                self.label_9f.setText("满载")
            else:
                self.label_9f.setText("未满载")

            if self.UIinformation["fullLoadGarbage"][1] == True:
                self.label_10f.setText("满载")
            else:
                self.label_10f.setText("未满载")

            if self.UIinformation["fullLoadGarbage"][3] == True:
                self.label_11f.setText("满载")
            else:
                self.label_11f.setText("未满载")

            if self.UIinformation["fullLoadGarbage"][0] == True:
                self.label_12f.setText("满载")
            else:
                self.label_12f.setText("未满载")

    def showImage(self):
        img = cv2.imread("img//4.png")
        if img is None:
            return
        image_show = cv2.resize(img, (520, 150))  # 把读到的帧的大小重新设置为 520*150
        width, height = image_show.shape[:2]  # 行:宽，列:高
        image_show = cv2.cvtColor(
            image_show, cv2.COLOR_BGR2RGB
        )  # opencv读的通道是BGR,要转成RGB
        self.showImage1 = QtGui.QImage(
            image_show.data, height, width, QImage.Format_RGB888
        )
        self.label_16.setPixmap(QPixmap.fromImage(self.showImage1))

    def showImage_2(self):
        img = cv2.imread("img//5.png")
        if img is None:
            return
        image_show = cv2.resize(img, (180, 150))  # 把读到的帧的大小重新设置为 600*360
        width, height = image_show.shape[:2]  # 行:宽，列:高
        image_show = cv2.cvtColor(
            image_show, cv2.COLOR_BGR2RGB
        )  # opencv读的通道是BGR,要转成RGB
        self.showImage3 = QtGui.QImage(
            image_show.data, height, width, QImage.Format_RGB888
        )
        self.label_17.setPixmap(QPixmap.fromImage(self.showImage3))

    def showVideo(self):
        if self.flag == True:
            image_show = cv2.resize(self.img, (700, 350))
            width, height = image_show.shape[:2]  # 行:宽，列:高
            image_show = cv2.cvtColor(
                image_show, cv2.COLOR_BGR2RGB
            )  # opencv读的通道是BGR,要转成RGB
            self.showImage2 = QtGui.QImage(
                image_show.data, height, width, QImage.Format_RGB888
            )
            self.label_15.setPixmap(QPixmap.fromImage(self.showImage2))
        else:
            print("the img is error")

    def getImg(self):
        while True:
            self.cap = cv2.VideoCapture("img//1.mov")
            while True:
                self.flag, self.frame = self.cap.read()
                if self.flag:
                    self.img = self.frame
                    time.sleep(0.035)
                else:
                    break


# for test
def UIQ_put(UIQ, UIinformation):
    while True:
        time.sleep(0.025)
        UIQ.put(UIinformation)
        print("the information has put")


if __name__ == "__main__":
    UIinformation = {
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
    UIQ = Queue(1)#全局变量尽量少用
    # subprocess = Process(target=UIQ_put, args=(UIQ, copy.deepcopy(UIinformation)))
    subprocess = Process(target=UIQ_put, args=(UIQ, UIinformation))
    subprocess.start()
    app = QApplication(sys.argv)
    UI_object = showUI(UIQ=UIQ)
    UI_object.setupUi()
    app.exec_()
