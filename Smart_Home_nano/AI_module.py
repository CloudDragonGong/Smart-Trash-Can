import cv2
import torchvision.transforms as transforms
import torch
import os
import numpy as np
from PIL import Image
from PIL import ImageFile
import onnxruntime

# 神经网络参数初始化
ImageFile.LOAD_TRUNCATED_IMAGES = True

# %matplotlib inline
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


class Resnet:
    def __init__(self, load_path="resnet50.onnx"):
        self.load_path = load_path
        print("模型开始加载")
        if self.load_path is not None:
            self.model = onnxruntime.InferenceSession(load_path)
        else:
            print('test model return flag= 5 ')
        print("模型加载结束")

    def classify(self, frame):
        if self.load_path is not None:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img = img.convert("RGB")
            img = self.padding_black(img)

            loader = transforms.Compose([transforms.ToTensor()])
            img = loader(img)
            return self.gar_sort(img)
        else:
            return 5

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

    def gar_sort(self, image):
        # 对处理好的图片进行模型预测
        src = image.numpy()
        src = src.reshape(3, 224, 224)
        src = np.transpose(src, (1, 2, 0))
        image = torch.unsqueeze(image, dim=0)
        image = image.numpy()
        ort_input = {"input": image}
        print("分类开始")
        pred = self.model.run(["output"], ort_input)[0][0]

        # print(pred.dtype)
        score = self.softmax(pred)
        pred_id = np.argmax(score)
        print(pred_id)
        if pred_id >=0 and pred_id <15 :
            flag = 0
        elif pred_id >=15 and pred_id < 23:
            flag = 1
        elif pred_id >= 23 and pred_id < 52:
            flag = 2
        elif pred_id >= 52 and pred_id < 63:
            flag = 3
        else:
            flag = 4
        print("分类完成")
        return flag
