#库

from multiprocessing import Queue, Process
import  threading 
import cv2
import numpy as np
import time
import math 


import os



import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMessageBox
#from open_camera import Ui_MainWindow
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
from PyQt5.QtCore import QTimer,QDateTime


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







ser=serial.Serial('/dev/ttyUSB0',9600,timeout=0.5)
#ser.open()

ImageFile.LOAD_TRUNCATED_IMAGES = True

# %matplotlib inline
os.environ["CUDA_VISIBLE_DEVICES"] = "0"







#全局变量
UIinformation = { 'garbageCategory':None ,'fullLoad':False,'ifSuccess':False,
'TotalNumber':0}
UIQ = Queue(1)
cameraPath = 0
maskPath = 'img//mask.jpg'
NN=0
detect=0
#函数


def padding_black(img):

    w, h = img.size

    scale = 224. / max(w, h)
    img_fg = img.resize([int(x) for x in [w * scale, h * scale]])

    size_fg = img_fg.size
    size_bg = 224

    img_bg = Image.new("RGB", (size_bg, size_bg))

    img_bg.paste(img_fg, ((size_bg - size_fg[0]) // 2,
                          (size_bg - size_fg[1]) // 2))

    img = img_bg

    return img






def softmax(x):
    exp_x = np.exp(x)
    softmax_x = exp_x / np.sum(exp_x, 0)
    return softmax_x





def gar_sort(image):

    
    #对处理好的图片进行模型预测
    src = image.numpy()
    src = src.reshape(3, 224, 224)
    src = np.transpose(src, (1, 2, 0))
    image = torch.unsqueeze(image,dim=0)
    image = image.cuda()
    print('分类开始')
    pred = model(image)
    
    pred = pred.data.cpu().numpy()[0]
    #print(pred.dtype)
    score = softmax(pred)
    pred_id = np.argmax(score)
    print(pred_id)
    if pred_id==1 or pred_id==2:
        flag=0
    elif pred_id>=3 and pred_id<=5:
        flag=1
    elif pred_id>=6 and pred_id<=7:
        flag=2
    elif pred_id>=8 and pred_id<=9:
        flag=3	


    print('分类完成')
    return flag




           

def cut(img,box):
    pt1,pt2,pt3,pt4 = box 
    mask = img[pt1[1]:pt4[1],pt1[0]:pt2[0]]
    return mask 


def unevenLightCompensate(img, blockSize):
    if len(img.shape) == 2:
        gray = img
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    average = np.mean(gray)
    rows_new = int(np.ceil(gray.shape[0] / blockSize))
    cols_new = int(np.ceil(gray.shape[1] / blockSize))

    blockImage = np.zeros((rows_new, cols_new), dtype=np.float32)
    for r in range(rows_new):
        for c in range(cols_new):
            rowmin = r * blockSize
            rowmax = (r + 1) * blockSize
            if (rowmax > gray.shape[0]):
                rowmax = gray.shape[0]
            colmin = c * blockSize
            colmax = (c + 1) * blockSize
            if (colmax > gray.shape[1]):
                colmax = gray.shape[1]

            imageROI = gray[rowmin:rowmax, colmin:colmax]
            temaver = np.mean(imageROI)
            blockImage[r, c] = temaver
    blockImage = blockImage - average
    blockImage2 = cv2.resize(blockImage, (gray.shape[1], gray.shape[0]), interpolation=cv2.INTER_CUBIC)
    gray2 = gray.astype(np.float32)
    dst = gray2 - blockImage2
    dst[dst > 255] = 255
    dst = dst.astype(np.uint8)
    dst = cv2.GaussianBlur(dst, (7, 7), 0)

    return dst






def edge_demo(image):
    edge_output = cv2.Canny(image, 50, 100)
    return edge_output






def smooth(image):

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 35))
    closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    closed = cv2.erode(closed, None, iterations=10)
    closed = cv2.dilate(closed, None, iterations=10)
    cnts, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(cnts) == 0:
        return None, None
    c = sorted(cnts, key=cv2.contourArea, reverse=True)[0]

    # compute the rotated bounding box of the largest contour
    rect = cv2.minAreaRect(c)
    box = np.int0(cv2.boxPoints(rect))
    # draw a bounding box arounded the detected barcode and display the image
    # print ('smooth'+str(rect))
    return box, rect




num0=0

def detectSpam(frame,frame2,maskPath):

    cv2.imwrite('img//frame.jpg',frame)
    global num0
    global detect
    mask = cv2.imread(maskPath)
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    mask = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
    rows1,cols1 = frame.shape 
    mask = mask[0:rows1,0:cols1]
    # frame = cv2.bitwise_and(frame,frame,mask = mask)
    #dst = unevenLightCompensate(frame, 16)
    edge = edge_demo(frame)
    cv2.imwrite('img//edge1.jpg',edge)
    num1 = cv2.countNonZero(src=edge)

    #dst = unevenLightCompensate(frame2, 16)
    edge = edge_demo(frame2)
    cv2.imwrite('img//edge2.jpg',edge)
    num2 = cv2.countNonZero(src=edge)


    num = num1+num2
    #print ('the number of NUM of the contour =%s'%(num))
    #print ('the number of NUM0 of the contour =%s'%(num0))
    if num0==0:
        num0=num
    delta=num
    print('contour =%s'%(delta))
    if delta >8150:
        #print('contour =%s'%(delta))
        num0=num
        detect=detect+1
        if detect>=1:
            detect=0
            return True
        else:
            return False
    else :
        num0=num
        detect=0
        return False 

def Module(frame):
    
    img = Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
    img = img.convert('RGB')
    img = padding_black(img)

    loader = transforms.Compose([transforms.ToTensor()])
    img =loader(img)
    return gar_sort(img)












#类




class RWlock(object):
    def __init__(self):
        self._lock = threading.Lock()
        self._extra = threading.Lock()
        self.write_num = 0
 
    def write_acquire(self):
        with self._extra:
            self.write_num += 1
            if self.write_num == 1:
                self._lock.acquire()
                #print('write_acquire')
 
    def write_release(self):
        with self._extra:
            self.write_num -= 1
            if self.write_num == 0:
                self._lock.release()
                #print('wirte_release')
 
    def read_acquire(self):
        self._lock.acquire()
        #print('read_acquire')
 
    def read_release(self):
        self._lock.release()
        #print('read_release')

Lock = RWlock()















class Vision_Module():

    def __init__(self,q):
        self.detect=0
        self.if20s=True
        self.frame=None
        self.frame2=None
        self.cap = cv2.VideoCapture(cameraPath)
        self.cap2=cv2.VideoCapture(1)
        self.ifGarbage = False  
        self.frameOut=None
        self.garbageType=None
        self.totalNum = 0 
        self.ifSuccess=False
        self.ifCompress = False
        self.fullLoad= False
        self.kitchen_Waste = 0
        self.recyclable_Trash = 0 
        self.hazardous_Waste = 0 
        self.other_Garbage = 0 
        self.trigger=False
        self.iftrigger=True
        self.qUIinformation={'garbageCategory':None ,'fullLoad':False,'ifSuccess':False,
        'TotalNumber':0,'Kitchen waste':0,'recyclable trash':0,'hazardous waste':0,'other garbage':0
        ,'serialOfGarbage':None,'ifBegin':False,'fullLoadGarbage':None,'fullLoadGarbage20s':False,'countDown':0}
        self.UIq = q 



    def camera(self):
        reg,self.frame =self.cap.read()
        cv2.imwrite('img//1.jpg',self.frame)
        reg,self.frame2=self.cap2.read()
        #cv2.imwrite('img//2.jpg',self.frame2)




    
    def detectionModule(self):
        return detectSpam(self.frame,self.frame2,maskPath = maskPath)




    
    def CVModule(self):
        self.qUIinformation['ifBegin'] = True
        img = self.frame

        #####由于硬件优化改变，完全不需要视觉处理##########


        # mask  = cv2.imread(maskPath)

        # #必须是相同的大小的图片才可以
        # imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        # mask = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)

        # rows1,cols1 = imgGray.shape
        # mask = mask[0:rows1,0:cols1]

        # ret,mask = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY)
        # #img = cv2.bitwise_and(img,img,mask = mask)
        # imgUnevenLight = unevenLightCompensate (img , 16)
        # imgEdge = edge_demo(imgUnevenLight)
        # box,imgSmooth = smooth(imgEdge)
        # if  box  is None:
        #     print('cutOut box error')
        #     return 
        # # imgOut= cut(img,box)
        # if  imgOut  is None:
        #     print('cutOut error')
        #     return 

        #############################################
        imgOut=img
        self.frameOut = imgOut
        cv2.imwrite('img//imgOut.jpeg',imgOut)
        self.qUIinformation['ifBegin'] = True
        self.qUIinformation['ifSuccess'] = False
    





    def AIModule(self):
        self.frameOut=cv2.imread("img//1.jpg")
        flag  = Module(self.frameOut)
        print('flag='+str(flag))
        
        if flag == 0 : 
            self.garbageType = '其他垃圾'
            self.other_Garbage += 1 
        if flag == 1 : 
            self.garbageType = '厨余垃圾'
            self.kitchen_Waste += 1 
        if flag == 2 : 
            self.garbageType = '可回收垃圾'
            self.recyclable_Trash+=1 
        if flag == 3 :
            self.garbageType = '有害垃圾'
            self.hazardous_Waste+= 1 
        
        self.qUIinformation['serialOfGarbage'] = flag
        self.qUIinformation['ifBegin'] = True
        self.qUIinformation['ifSuccess'] = True
        print('AIModule done')






    def UI_pass_parameters_1(self):
        Lock.write_acquire()
        self.qUIinformation['fullLoad']=self.fullLoad
        self.qUIinformation['ifSuccess']=self.ifSuccess=True
        self.qUIinformation['garbageCategory']=self.garbageType
        self.qUIinformation['Kitchen waste'] = self.kitchen_Waste
        self.qUIinformation['recyclable trash'] = self.recyclable_Trash
        self.qUIinformation['hazardous waste'] = self.hazardous_Waste
        self.qUIinformation['other garbage'] = self.other_Garbage
        self.totalNum+=1
        self.qUIinformation['TotalNumber']=self.totalNum
        self.UIq.put(self.qUIinformation)
        Lock.write_release()
        #print('UI pass 1 done')
    






    def sendSerialInformation(self):
        print('正在发送数据')
        
        data=[[0x2c],[0x12],[0x00],[0x5B]]
        if(self.garbageType=='其他垃圾'):
            data[2]=[0x00]
        elif(self.garbageType=='厨余垃圾'):
            data[2]=[0x01]
        elif(self.garbageType=='可回收垃圾'):
            data[2]=[0x02]
        elif(self.garbageType=='有害垃圾'):
            data[2]=[0x03]
        else:
            print('error')
            exit()
        for i in range(0,4):
            data[i]=bytearray(data[i])
            time.sleep(0.1)
            print(data[i])
            ser.write(data[i])
        print('sendSerialInformation done')






    def determineCompress(self):
        print('determineCompress have done')


    def recv(self):
        while True:
            data=ser.read(1)
            print(data)
            if data==b'':
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
        self.qUIinformation['fullLoad']=self.fullLoad
        self.qUIinformation['ifBegin'] = False
        self.UIq.put(self.qUIinformation)
        #print('UI pass 0 done')
    






    def UI_pass_parameters_0(self):


        self.qUIinformation['garbageCategory']=None
        self.qUIinformation['Kitchen waste'] = self.kitchen_Waste
        self.qUIinformation['recyclable trash'] = self.recyclable_Trash
        self.qUIinformation['hazardous waste'] = self.hazardous_Waste
        self.qUIinformation['other garbage'] = self.other_Garbage
        self.qUIinformation['ifSuccess']=self.ifSuccess=False
        self.qUIinformation['TotalNumber']=self.totalNum
        self.qUIinformation['fullLoad']=self.fullLoad

        self.UIq.put(self.qUIinformation)
        #print('UI pass 0 done')







    def UI_pass_parameters_3(self):
        print('UI_pass_parameters_3 开始')
        while self.qUIinformation['ifBegin'] == True and self.qUIinformation['ifSuccess'] == False :
            self.qUIinformation['garbageCategory']=None
            self.qUIinformation['Kitchen waste'] = self.kitchen_Waste
            self.qUIinformation['recyclable trash'] = self.recyclable_Trash
            self.qUIinformation['hazardous waste'] = self.hazardous_Waste
            self.qUIinformation['other garbage'] = self.other_Garbage
            self.qUIinformation['TotalNumber']=self.totalNum
            self.qUIinformation['fullLoad']=self.fullLoad

            self.UIq.put(self.qUIinformation)


        #print('UI pass 3 done')










    def UI_pass_parameters_4(self):
        #print('UI_pass_parameters_4 开始')

        while self.qUIinformation['ifBegin'] == True and self.qUIinformation['ifSuccess'] == True :
            
            self.qUIinformation['garbageCategory']=self.garbageType
            self.qUIinformation['Kitchen waste'] = self.kitchen_Waste
            self.qUIinformation['recyclable trash'] = self.recyclable_Trash
            self.qUIinformation['hazardous waste'] = self.hazardous_Waste
            self.qUIinformation['other garbage'] = self.other_Garbage
            self.qUIinformation['TotalNumber']=self.totalNum
            self.UIq.put(self.qUIinformation)

        #print('UI pass 4 done')








    def countDown(self):
        while True:
            i=0
            if self.iftrigger:
                for i in range(0,20):
                    time.sleep(1)
                    self.qUIinformation['countDown']=i+1
                    if(self.trigger):
                        #阻塞（规范代码应该写专门的阻塞函数，后续需要优化）
                        while self.trigger:
                            a=10 #优化
                        self.trigger=False
                        break
                if(not self.trigger and i==19):
                    self.if20s=False
                    self.sendSerialOfTrigger()
                    self.waitingForSerial()







    def sendSerialOfTrigger(self):

        data=[[0x5D],[0x30],[0x01],[0x2A]]
        for i in range(0,4):
            data[i]=bytearray(data[i])
            print(data[i])
            time.sleep(0.1)
            ser.write(data[i])

        print("sendSerialOfTrigger has done")
        self.trigger=False
        self.iftrigger=False







    def run(self):
        global NN
        global detect
        #一定时间检测满载情况线程
        t0 = threading.Thread(target=self.countDown,args=())
        t0.start()

        while True:
            self.cap.open(0)
            self.cap2.open(1)
            self.camera()
            if not self.detectionModule():
                self.UI_pass_parameters_0()
            elif self.if20s:
                detect=-1
                NN=NN+1
                self.cap.release()
                self.cap2.release()
                self.trigger=True
                #time.sleep(0.5)
                self.cap.open(0)

                self.camera()
                self.cap.release()

                t1 = threading.Thread(target = self.UI_pass_parameters_3,args =())
                t2 = threading.Thread(target = self.UI_pass_parameters_4,args=())

                self.CVModule()
                t1.start()
                self.AIModule()
                self.UI_pass_parameters_1()
        
                t2.start()
                self.sendSerialInformation()
                try:
                    if self.waitingForSerial():
                        self.UI_pass_parameters_2()
                except:
                    self.fullLoad = False
                    self.qUIinformation['fullLoad'] = False
                    self.qUIinformation['ifBegin'] = False
                    self.qUIinformation['ifSuccess'] = True
                
                self.fullLoad = False
                self.trigger=False
                self.iftrigger=True
                if NN==0:
                    self.frame=None
                    self.cap = cv2.VideoCapture(cameraPath)
                    self.ifGarbage = False
                    self.frameOut=None
                    self.garbageType=None
                    self.totalNum = 0
                    self.ifSuccess=False
                    self.ifCompress = False
                    self.fullLoad= False
                    self.kitchen_Waste = 0
                    self.recyclable_Trash = 0
                    self.hazardous_Waste = 0
                    self.other_Garbage = 0
                    self.trigger=False
                    self.iftrigger=True
                    self.qUIinformation={'garbageCategory':None ,'fullLoad':False,'ifSuccess':False,
        'TotalNumber':0,'Kitchen waste':0,'recyclable trash':0,'hazardous waste':0,'other garbage':0
        ,'serialOfGarbage':None,'ifBegin':False,'fullLoadGarbage':None,'fullLoadGarbage20s':False,'countDown':0}
                    

                else:
                    continue
            




















class showUI(QtWidgets.QMainWindow):


    def __init__ (self):
        super().__init__()
        self.initUI()
        self.flag = False 
        self.img = None 
        self.UIflag = 0 




    def initUI(self):

        desktop = QApplication.desktop()


        font = QtGui.QFont() 
        font.setFamily('微软雅黑')
        font.setBold(True) 
        font.setPointSize(20) 
        font.setWeight(100) 




        self.main_widget = QtWidgets.QWidget()  # 创建窗口主部件
        self.main_layout = QtWidgets.QGridLayout()  # 创建主部件的网格布局
        self.main_widget.setLayout(self.main_layout)  # 设置窗口主部件布局为网格布局

        ###########上面的部件#######
        self.On_widget = QtWidgets.QWidget()
        self.On_widget.setObjectName('On_widget')
        self.On_layout = QtWidgets.QGridLayout() 
        self.On_widget.setLayout(self.On_layout)
        self.On_widget.setStyleSheet('''QWidget{border-radius:7px;background-color:#ee0000;}''')
        ##########中间的部件##############
        self.Md_widget = QtWidgets.QWidget()
        self.Md_widget.setObjectName('Md_widget')
        self.Md_layout = QtWidgets.QGridLayout() 
        self.Md_widget.setLayout(self.Md_layout)
        self.Md_widget.setStyleSheet('''QWidget{border-radius:7px;background-color:#66FFCC;}''')
        ############下面的步见################
        self.Dn_widget = QtWidgets.QWidget()
        self.Dn_widget.setObjectName('Dn_widget')
        self.Dn_layout = QtWidgets.QGridLayout() 
        self.Dn_widget.setLayout(self.Dn_layout)
        self.Dn_widget.setStyleSheet('''QWidget{border-radius:7px;background-color:#28B464;}''')



        self.main_layout.addWidget(self.On_widget,0,6,2,5)      
        self.main_layout.addWidget(self.Md_widget,3,6,8,5)     
        self.main_layout.addWidget(self.Dn_widget,12,6,4,5)     

        self.setCentralWidget(self.main_widget)     # 设置窗口主部件
        self.main_widget.setStyleSheet('''QWidget{border-radius:7px;background-color:#66CCFF;}''')





        self.label_0 = QtWidgets.QLabel(self) #用来显示垃圾类别
        self.label_0.setFont(font)
        self.label_0.resize(desktop.width()*0.4, desktop.height()*0.1)
        self.label_0.move(desktop.width()*0.85, desktop.height()*0.00)





        self.label_1 = QtWidgets.QLabel(self) #用来显示可回收垃圾
        self.label_1.setFont(font)
        self.label_1.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_1.move(desktop.width()*0.67, desktop.height()*0.1)

        self.label_2 = QtWidgets.QLabel(self) #用来显示厨余垃圾
        self.label_2.setFont(font)
        self.label_2.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_2.move(desktop.width()*0.67, desktop.height()*0.23)

        self.label_3 = QtWidgets.QLabel(self) #用来显示其他垃圾
        self.label_3.setFont(font)
        self.label_3.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_3.move(desktop.width()*0.67, desktop.height()*0.49)

        
        self.label_13= QtWidgets.QLabel(self) #用来显示有害垃圾
        self.label_13.setFont(font)
        self.label_13.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_13.move(desktop.width()*0.67, desktop.height()*0.36)





        self.label_4 = QtWidgets.QLabel(self) #用来显示是否完成分类
        self.label_4.setFont(font)
        self.label_4.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_4.move(desktop.width()*0.7, desktop.height()*0.62)

        self.label_5 = QtWidgets.QLabel(self) #用来显示success or false
        self.label_5.setFont(font)
        self.label_5.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_5.move(desktop.width()*0.9, desktop.height()*0.62)


        self.label_6 = QtWidgets.QLabel(self) #用来显示是否满载
        self.label_6.setFont(font)
        self.label_6.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_6.move(desktop.width()*0.7, desktop.height()*0.75)

        self.label_7 = QtWidgets.QLabel(self) #用来显示满载true or false
        self.label_7.setFont(font)
        self.label_7.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_7.move(desktop.width()*0.9, desktop.height()*0.75)


        self.label_8 = QtWidgets.QLabel(self) #用来显示所有垃圾总数
        self.label_8.setFont(font)
        self.label_8.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_8.move(desktop.width()*0.76, desktop.height()*0.015)

        self.label_8_1 = QtWidgets.QLabel(self) #用来显示 序号
        self.label_8_1.setFont(font)
        self.label_8_1.resize(desktop.width()*0.4,desktop.height()*0.1)
        self.label_8_1.move(desktop.width()*0.75,desktop.height()*0.0)




        self.label_9 = QtWidgets.QLabel(self) #用来显示可回收垃圾总数
        self.label_9.setFont(font)
        self.label_9.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_9.move(desktop.width()*0.83, desktop.height()*0.1)


        self.label_10 = QtWidgets.QLabel(self) #用来显示厨余垃圾总数
        self.label_10.setFont(font)
        self.label_10.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_10.move(desktop.width()*0.83, desktop.height()*0.23)

        self.label_11= QtWidgets.QLabel(self) #用来显示有害垃圾总数
        self.label_11.setFont(font)
        self.label_11.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_11.move(desktop.width()*0.83, desktop.height()*0.36)

        self.label_12= QtWidgets.QLabel(self) #用来显示其他垃圾总数
        self.label_12.setFont(font)
        self.label_12.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_12.move(desktop.width()*0.83, desktop.height()*0.49)





        #####显示是否满载############
        self.label_9f = QtWidgets.QLabel(self) #用来显示可回收垃圾是否满载
        self.label_9f.setFont(font)
        self.label_9f.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_9f.move(desktop.width()*0.9, desktop.height()*0.1)


        self.label_10f = QtWidgets.QLabel(self) #用来显示厨余垃圾是否满载
        self.label_10f.setFont(font)
        self.label_10f.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_10f.move(desktop.width()*0.9, desktop.height()*0.23)

        self.label_11f= QtWidgets.QLabel(self) #用来显示有害垃圾是否满载
        self.label_11f.setFont(font)
        self.label_11f.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_11f.move(desktop.width()*0.9, desktop.height()*0.36)

        self.label_12f= QtWidgets.QLabel(self) #用来显示其他垃圾是否满载
        self.label_12f.setFont(font)
        self.label_12f.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_12f.move(desktop.width()*0.9, desktop.height()*0.49)









        self.label_14= QtWidgets.QLabel(self) #用来显示 垃圾的类别
        self.label_14.setFont(font)
        self.label_14.resize(desktop.width()*0.4, desktop.height()*0.2)
        self.label_14.move(desktop.width()*0.85, desktop.height()*0.01)

        self.label_15= QtWidgets.QLabel(self) #用来显示视频
        self.label_15.resize(desktop.width()*0.65, desktop.height()*0.65)
        self.label_15.move(desktop.width()*0.0, desktop.height()*0.00)

        self.label_16= QtWidgets.QLabel(self) #用来显示是否完成的图像
        self.label_16.resize(desktop.width()*0.50, desktop.height()*0.65)
        self.label_16.move(desktop.width()*0.00, desktop.height()*0.49)

        self.label_17= QtWidgets.QLabel(self) #用来显示垃圾种类的图像
        self.label_17.resize(desktop.width()*0.3, desktop.height()*0.3)
        self.label_17.move(desktop.width()*0.50, desktop.height()*0.665)

        self.label_18= QtWidgets.QLabel(self) #用来显示“倒计时”
        self.label_18.setFont(font)
        self.label_18.resize(desktop.width()*0.4, desktop.height()*0.1)
        self.label_18.move(desktop.width()*0.665, desktop.height()*0.0)

        self.label_19= QtWidgets.QLabel(self) #用来显示倒计时数字
        self.label_19.setFont(font)
        self.label_19.resize(desktop.width()*0.4, desktop.height()*0.1)
        self.label_19.move(desktop.width()*0.68, desktop.height()*0.05)
        
        self.label_20=QtWidgets.QLabel(self)#显示小格式序号
        self.label_20.resize(desktop.width()*0.2,desktop.height()*0.1)
        self.label_20.move(desktop.width()*0.7,desktop.height()*0.75)

        self.label_21=QtWidgets.QLabel(self)#显示小格式垃圾种类
        self.label_21.resize(desktop.width()*0.2,desktop.height()*0.1)
        self.label_21.move(desktop.width()*0.7,desktop.height()*0.78)

        self.label_22=QtWidgets.QLabel(self)#显示小格式数量
        self.label_22.resize(desktop.width()*0.2,desktop.height()*0.1)
        self.label_22.move(desktop.width()*0.7,desktop.height()*0.81)

        self.label_23=QtWidgets.QLabel(self)#显示小格式分类成功与否
        self.label_23.resize(desktop.width()*0.2,desktop.height()*0.1)
        self.label_23.move(desktop.width()*0.7,desktop.height()*0.85)

        self.label_24=QtWidgets.QLabel(self)#显示  总数
        self.label_24.resize(desktop.width()*0.2,desktop.height()*0.1)
        self.label_24.move(desktop.width()*0.82,desktop.height()*0.76)

        self.label_25=QtWidgets.QLabel(self)#显示小格式 垃圾种类
        self.label_25.resize(desktop.width()*0.2,desktop.height()*0.1)
        self.label_25.move(desktop.width()*0.82,desktop.height()*0.79)

        self.label_26=QtWidgets.QLabel(self)#显示小格式 同种数量
        self.label_26.resize(desktop.width()*0.2,desktop.height()*0.1)
        self.label_26.move(desktop.width()*0.82,desktop.height()*0.82)

        self.label_27=QtWidgets.QLabel(self)#显示小格式 分类成功与否
        self.label_27.resize(desktop.width()*0.2,desktop.height()*0.1)
        self.label_27.move(desktop.width()*0.82,desktop.height()*0.86)

        self.setWindowTitle('垃圾桶工作状态')
        self.setGeometry(600, 600, 1000, 500)
        self.showMaximized()




    def setupUi(self):

        self.Timer1=QTimer()     #自定义QTimer
        showVideoThread = threading.Thread(target = self.getImg)
        showVideoThread.setDaemon(True)
        showVideoThread.start()
        self.Timer1.start(0.035)   #每0.035秒运行一次
        self.Timer1.timeout.connect(self.showVideo)
        self.Timer1.timeout.connect(self.update)   #连接update
        self.Timer1.timeout.connect(self.showImage)
        self.Timer1.timeout.connect(self.showImage_2)
        QtCore.QMetaObject.connectSlotsByName(self)




    def yunUI1(self):
        img = cv2.imread('img//g.png')
        cv2.imwrite('img//4.png',img)  
        img = cv2.imread('img//a.png')
        cv2.imwrite('img//5.png',img)  
        





    def yunUI2(self):
        img = cv2.imread('img//2.png')
        cv2.imwrite('img//4.png',img)  
        if self.UIflag >= 0 and self.UIflag <=10  : 
            img = cv2.imread('img//h1.png')
            self.UIflag+=1 
        elif self.UIflag > 10 and self.UIflag <=20 :
            img = cv2.imread('img//h2.png')
            self.UIflag+=1 

        elif self.UIflag >20 and self.UIflag <=30 :
            img = cv2.imread('img//h3.png')
            self.UIflag+=1 

        elif self.UIflag > 30 and self.UIflag <=40 :
            img = cv2.imread('img//h4.png')
            self.UIflag+=1
        else:
            img = cv2.imread('img//h4.png')
            self.UIflag -= 41
        cv2.imwrite('img//5.png',img)







    def yunUI3(self):
        img = cv2.imread('img//3.png')
        cv2.imwrite('img//4.png',img)  
        if self.UIinformation['serialOfGarbage'] == 1:
                img = cv2.imread('img//b.png')
        elif self.UIinformation['serialOfGarbage'] == 3:
                img = cv2.imread('img//c.png')
        elif self.UIinformation['serialOfGarbage'] == 2:
                img = cv2.imread('img//d.png')
        else :
                img = cv2.imread('img//e.png')
        cv2.imwrite('img//5.png',img)








    def update(self):
        
        self.UIinformation =  UIQ.get()
        
        if self.UIinformation['ifBegin'] == False and self.UIinformation['ifSuccess'] == False :
            self.yunUI1()
        elif self.UIinformation['ifBegin'] == True and self.UIinformation['ifSuccess'] == False :
            self.yunUI2()
        elif self.UIinformation['ifBegin'] == True and self.UIinformation['ifSuccess'] == True :
            self.yunUI3()
            




        self.label_0.setText('垃圾种类')
        self.label_1.setText('可回收垃圾')
        self.label_2.setText('厨余垃圾')
        self.label_3.setText('其他垃圾')
        self.label_4.setText('分类成功与否')
        if self.UIinformation['ifSuccess']:
            self.label_5.setText('OK!')
        else:
            self.label_5.setText('不OK!')

        #self.label_5.setText(str(self.UIinformation['ifSuccess']))
        #self.label_6.setText('是否满载')
        #self.label_7.setText(str(self.UIinformation['fullLoad']))
        self.label_8.setText(str(self.UIinformation['TotalNumber']))
        self.label_8_1.setText('序号')
        self.label_9.setText(str(self.UIinformation['recyclable trash']))
        self.label_10.setText(str(self.UIinformation['Kitchen waste']))
        self.label_11.setText(str(self.UIinformation['hazardous waste']))
        self.label_12.setText(str(self.UIinformation['other garbage']))
        self.label_13.setText('有害垃圾')
        self.label_14.setText(self.UIinformation['garbageCategory'])
        self.label_18.setText('倒计时')
        self.label_19.setText(str(20-self.UIinformation['countDown']))


        self.label_20.setText('序号')
        self.label_21.setText('垃圾种类')
        self.label_22.setText('数量')
        self.label_23.setText('分类成功与否')

        if self.UIinformation['ifSuccess']:
            self.label_24.setText(str(self.UIinformation['TotalNumber']))
            self.label_25.setText(self.UIinformation['garbageCategory'])

            if self.UIinformation['garbageCategory']=='可回收垃圾':
                self.label_26.setText(str(self.UIinformation['recyclable trash']))
            elif self.UIinformation['garbageCategory']=='厨余垃圾':
                self.label_26.setText(str(self.UIinformation['Kitchen waste']))
            elif self.UIinformation['garbageCategory']=='有害垃圾':
                self.label_26.setText(str(self.UIinformation['hazardous waste']))
            elif self.UIinformation['garbageCategory']=='其他垃圾':
                self.label_26.setText(str(self.UIinformation['other garbage']))
        else:
            self.label_24.setText('')
            self.label_25.setText('')
            self.label_26.setText('')
        
        
        if self.UIinformation['ifSuccess']:
            self.label_27.setText('OK!')
        else:
            self.label_27.setText('不OK!')



        if not self.UIinformation['fullLoadGarbage20s']:
            if self.UIinformation['fullLoadGarbage']==None: 
                a=0

            elif self.UIinformation['fullLoadGarbage']==2:
                self.label_9f.setText('未满载')

            elif self.UIinformation['fullLoadGarbage']==1:
                self.label_10f.setText('未满载')

            elif self.UIinformation['fullLoadGarbage']==3:
                self.label_11f.setText('未满载')

            elif self.UIinformation['fullLoadGarbage']==0:
                self.label_12f.setText('未满载')

            elif self.UIinformation['fullLoadGarbage']==12:
                self.label_9f.setText('满载')

            elif self.UIinformation['fullLoadGarbage']==11:
                self.label_10f.setText('满载')

            elif self.UIinformation['fullLoadGarbage']==13:
                self.label_11f.setText('满载')

            elif self.UIinformation['fullLoadGarbage']==10:
                self.label_12f.setText('满载')

        else:
            if self.UIinformation['fullLoadGarbage'][2]==True:
                self.label_9f.setText('满载')
            else:
                self.label_9f.setText('未满载')

            if self.UIinformation['fullLoadGarbage'][1]==True:
                self.label_10f.setText('满载')
            else:
                self.label_10f.setText('未满载')

            if self.UIinformation['fullLoadGarbage'][3]==True:
                self.label_11f.setText('满载')
            else:
                self.label_11f.setText('未满载')
                
            if self.UIinformation['fullLoadGarbage'][0]==True:
                self.label_12f.setText('满载')
            else:
                self.label_12f.setText('未满载')







    def showImage(self):
        
        img = cv2.imread("img//4.png")
        if img is None :
            return 
        image_show = cv2.resize(img, (520, 150))  # 把读到的帧的大小重新设置为 520*150
        width, height = image_show.shape[:2]  # 行:宽，列:高
        image_show = cv2.cvtColor(image_show, cv2.COLOR_BGR2RGB)  # opencv读的通道是BGR,要转成RGB
        self.showImage1 = QtGui.QImage(image_show.data, height, width, QImage.Format_RGB888)
        self.label_16.setPixmap(QPixmap.fromImage(self.showImage1))










    def showImage_2(self):
        img = cv2.imread("img//5.png")
        if img is None :
            return 
        image_show = cv2.resize(img, (180,150 ))  # 把读到的帧的大小重新设置为 600*360
        width, height = image_show.shape[:2]  # 行:宽，列:高
        image_show = cv2.cvtColor(image_show, cv2.COLOR_BGR2RGB)  # opencv读的通道是BGR,要转成RGB
        self.showImage3 = QtGui.QImage(image_show.data, height, width, QImage.Format_RGB888)
        self.label_17.setPixmap(QPixmap.fromImage(self.showImage3))









    def showVideo(self):
        
        if( self.flag == True ):
            image_show = cv2.resize(self.img, (700,350)) 
            width, height = image_show.shape[:2]  # 行:宽，列:高
            image_show = cv2.cvtColor(image_show, cv2.COLOR_BGR2RGB)  # opencv读的通道是BGR,要转成RGB
            self.showImage2 = QtGui.QImage(image_show.data, height, width, QImage.Format_RGB888)
            self.label_15.setPixmap(QPixmap.fromImage(self.showImage2))
        else :
            print('error')




 
    def getImg(self):
        while True:
            self.cap  = cv2.VideoCapture('img//1.mov')
            while True:
                self.flag,self.frame = self.cap.read()
                if self.flag :
                    self.img = self.frame 
                    time.sleep(0.035)
                else :
                    break




def run_VM(q):
    LoadModel()
    VM = Vision_Module(q)
    VM.run()






def run_UI():
    app = QApplication(sys.argv)
    UI = showUI()
    UI.setupUi()
    app.exec_()






def LoadModel():
    print('模型开始加载')
    global model
    model = models.resnet18(pretrained=False)
    fc_inputs = model.fc.in_features
    model.fc = nn.Linear(fc_inputs, 216)
    model = model.cuda()
    # 加载训练好的模型
    checkpoint = torch.load('model_best_checkpoint_resnet181.pth.tar')
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()
    
    print('模型加载结束')








def updateUIinformation(UIinformation):
    while True:
        UIinformation = UIQ.get()
        print(UIinformation)








if __name__ == '__main__':
   
    p1 = Process(target=run_UI)
    p1.start()
    run_VM(UIQ)	 
    
    














        










