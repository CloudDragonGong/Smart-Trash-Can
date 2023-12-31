from multiprocessing import Queue, Process
import multiprocessing
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


# 文件间的import
import cv_module
import UI
import AI_module
from lock import Lock

# UI显示的字典
UIinformation = {
    "garbageCategory": None,
    "fullLoad": False,
    "ifSuccess": False,
    "TotalNumber": 0,
}

# 运行视觉模块
def run_VM(q, AI):
    AI.LoadModel()
    # AI_module.AIModule.LoadModel(load_path)
    VM = cv_module.Vision_Module(q=q,AI_module=AI)
    VM.run()


# 运行UI模块
def run_UI(UIQ):
    app = QApplication(sys.argv)
    UI_object = UI.showUI(UIQ)
    UI_object.setupUi()
    app.exec_()


if __name__ == "__main__":
    # 用于传输信息的消息队列
    UIQ = Queue(1)
    multiprocessing.freeze_support()
    load_path = "model_best_checkpoint_resnet181.pth.tar"
    p2 = Process(target=run_UI, args=(UIQ,))
    p2.start()
    AI = AI_module.AIModule(load_path=load_path)
    run_VM(UIQ, AI)
