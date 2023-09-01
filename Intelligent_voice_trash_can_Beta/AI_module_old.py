from multiprocessing import Queue, Process
import threading
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
import onnxruntime

# 神经网络参数初始化
ImageFile.LOAD_TRUNCATED_IMAGES = True

# %matplotlib inline
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


class AIModule:
    def __init__(self, load_path):
        self.load_path = load_path

    """
    def LoadModel(self):
        print("模型开始加载")
        global model
        model = models.resnet18(pretrained=False)
        fc_inputs = model.fc.in_features
        model.fc = nn.Linear(fc_inputs, 216)
        model = model.cuda()
        # 加载训练好的模型
        checkpoint = torch.load(self.load_path)
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        print("模型加载结束")
    """

    def LoadModel(self):
        print("模型开始加载")
        global model

        # 加载训练好的模型
        model = onnxruntime.InferenceSession("model_best_checkpoint_resnet181.onnx")

        print("模型加载结束")

    def Module(self, frame):
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img = img.convert("RGB")
        img = self.padding_black(img)

        loader = transforms.Compose([transforms.ToTensor()])
        img = loader(img)
        return self.gar_sort(img)

    def padding_black(self, img):
        w, h = img.size

        scale = 224.0 / max(w, h)
        img_fg = img.resize([int(x) for x in [w * scale, h * scale]])

        size_fg = img_fg.size
        size_bg = 224

        img_bg = Image.new("RGB", (size_bg, size_bg))

        img_bg.paste(img_fg, ((size_bg - size_fg[0]) // 2, (size_bg - size_fg[1]) // 2))

        img = img_bg

        return img

    def softmax(self, x):
        exp_x = np.exp(x)
        softmax_x = exp_x / np.sum(exp_x, 0)
        return softmax_x

    """
    def gar_sort(self, image):
        # 对处理好的图片进行模型预测
        src = image.numpy()
        src = src.reshape(3, 224, 224)
        src = np.transpose(src, (1, 2, 0))
        image = torch.unsqueeze(image, dim=0)
        image = image.cuda()
        print("分类开始")
        pred = model(image)

        pred = pred.data.cpu().numpy()[0]
        # print(pred.dtype)
        score = self.softmax(pred)
        pred_id = np.argmax(score)
        print(pred_id)
        if pred_id == 1 or pred_id == 2:
            flag = 0
        elif pred_id >= 3 and pred_id <= 5:
            flag = 1
        elif pred_id >= 6 and pred_id <= 7:
            flag = 2
        elif pred_id >= 8 and pred_id <= 9:
            flag = 3

        print("分类完成")
        return flag
    """

    def gar_sort(self, image):
        # 对处理好的图片进行模型预测
        src = image.numpy()
        src = src.reshape(3, 224, 224)
        src = np.transpose(src, (1, 2, 0))
        image = torch.unsqueeze(image, dim=0)
        image = image.numpy()
        ort_input = {"input": image}
        print("分类开始")
        pred = model.run(["output"], ort_input)[0][0]

        # print(pred.dtype)
        score = self.softmax(pred)
        pred_id = np.argmax(score)
        print(pred_id)
        if pred_id == 1 or pred_id == 2:
            flag = 0
        elif pred_id == 5:
            flag = 10
        elif pred_id >= 3 and pred_id <= 5:
            flag = 1
        elif pred_id >= 6 and pred_id <= 7:
            flag = 2
        elif pred_id >= 8 and pred_id <= 9:
            flag = 3

        print("分类完成")
        return flag
